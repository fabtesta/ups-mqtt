
class UpsMqttConfig:
    def __init__(self, config: dict):
        self.config = config
        self.mqtt_client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2)
        self.mqtt_client.username_pw_set(username=self.config["mqtt_user"], password=self.config["mqtt_pwd"])
        if str.lower(self.config["mqtt_tls"]) == 'true':
            self.mqtt_client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLSv1_2)

    config = ConfigParser(delimiters=('=',), inline_comment_prefixes=('#'))
    config.optionxform = str
    config.read(config_dir)

    cached_values = {}
    base_topic = config['MQTT'].get('base_topic', 'home/ups')
    if not base_topic.endswith('/'):
        base_topic += '/'

    ups_name = config['UPS'].get('name', 'ups')
    ups_host = config['UPS'].get('hostname', 'localhost')
    mqtt_host = config['MQTT'].get('hostname', 'localhost')
    mqtt_port = config['MQTT'].getint('port', 1883)
    mqtt_user = config['MQTT'].get('username', None)
    mqtt_password = config['MQTT'].get('password', None)
    interval = config['GENERAL'].getint('interval', 60)
    info_array = config['INFO']