from faststream.rabbit import RabbitQueue


INIT_BATTLE_QUEUE = RabbitQueue("init_battle")
BATTLE_STAR = RabbitQueue("battle_started")
