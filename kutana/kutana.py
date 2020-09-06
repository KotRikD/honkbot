from kutana.exceptions import ExitException
from kutana.structures import objdict
from kutana.executor import Executor
import asyncio
import asyncio_redis
#import uvloop

class Kutana:
    """Main class for constructing engine."""

    def __init__(self, executor=None, loop=None, redisconf=None):
        self.controllers = []
        self.executor = executor or Executor()

#        asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        self.loop = loop or asyncio.get_event_loop()
        #        self.loop.set_default_executor(ThreadPoolExecutor(1000))

        self.storage = {
            "controllers": {}
        }

        self.running = True
        self.loops = []
        self.tasks = []
        self.prcss = []
        self.gathered_loops = None

        self.redisconf = redisconf
        self.redisconn = None

        self.loop.run_until_complete(self.setup_redis_db())

    async def setup_redis_db(self):
        if not self.redisconn and self.redisconf:
            # Create Redis connection
#            nloop = asyncio.new_event_loop()
            transport, protocol = await self.loop.create_connection(asyncio_redis.RedisProtocol, self.redisconf['host'],
                                                               self.redisconf['port'])
            await protocol.auth(password=self.redisconf['password'])
            await protocol.select(2)
            self.redisconn = protocol

    def add_controller(self, controller, unique_name=None):
        """Adding controller to engine with target unique name if specified.
        If unique name is not specified pattern "{type}__{controllers_amount}"
        will be used.
        """

        if unique_name is None:
            unique_name = "{}__{}".format(
                controller.type,
                len(self.controllers)
            )

        self.storage["controllers"][unique_name] = controller

        self.controllers.append(controller)

    async def process_update(self, ctrl, update):
        """Prepare environment and process update from controller."""

        eenv = objdict(
            ctrl_type=ctrl.type,
            convert_to_message=ctrl.convert_to_message,
            dbredis=self.redisconn
        )


        await ctrl.setup_env(update, eenv)

        await self.executor(update, eenv)

    async def ensure_future(self, awaitable):
        """Shurtcut for asyncio.ensure_loop with curretn loop."""

        _awaitable = asyncio.ensure_future(awaitable, loop=self.loop)

        self.prcss.append(_awaitable)

        return _awaitable

    async def loop_for_controller(self, ctrl):
        """Receive and process updated from target controller."""

        receiver = await ctrl.get_receiver_coroutine_function()

        while self.running:
            for update in await receiver():
                await self.ensure_future(
                    self.process_update(
                        ctrl, update
                    )
                )

            await asyncio.sleep(0.01)

    def run(self):
        """Start engine."""

        asyncio.set_event_loop(self.loop)

        self.loops = []

        for controller in self.controllers:
            self.loops.append(self.loop_for_controller(controller))

            awaitables = self.loop.run_until_complete(
                controller.get_background_coroutines(self.ensure_future)
            )

            for awaitable in awaitables:
                self.loops.append(awaitable)

        self.loop.run_until_complete(
            self.executor(
                {
                    "kutana": self, "update_type": "startup",
                    "registered_plugins": self.executor.registered_plugins
                },
                objdict(ctrl_type="kutana")
            )
        )

        try:
            self.gathered = asyncio.gather(*self.loops, *self.tasks)

            self.loop.run_until_complete(self.gathered)
        except (KeyboardInterrupt, ExitException):
            pass

        self.loop.run_until_complete(self.dispose())

    async def dispose(self):
        """Free resources and prepare for shutdown."""

        await asyncio.gather(*self.prcss)

        await self.executor.dispose()

        for controller in self.controllers:
            await controller.dispose()
