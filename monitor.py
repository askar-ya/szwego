import time
import logic

# запускаем бесконечный цикл
while True:
    """проверяем новые товары"""
    data = logic.read_file()
    for shop in data:
        logic.pars_shop(shop)

    # спим 15 минут
    time.sleep(60*15)
