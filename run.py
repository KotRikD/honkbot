from kutana import *
import sentry_sdk

redisconf = {
    'host': "redis",
    'port': 6379,
    'db': 0,
    'password': 'pass'
}

kutana = Kutana(redisconf=redisconf)


# Creation
kutana.add_controller(
    VKController(load_configuration("vk_token", "configuration.json"))
)

# Load plugins from folder
kutana.executor.register_plugins(*load_plugins("plugin_need/"))
kutana.executor.register_plugins(*load_plugins("plugin_group/"))
kutana.executor.register_plugins(*load_plugins("plugins/"))

sentry_sdk.init("<my sentry dsn>")
# Start kutana
kutana.run()
