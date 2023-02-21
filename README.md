# wapp_youtube_wrapper

![](https://asdertasd.site/counter/wapp_youtube_wrapper)

Среда для поиска видеороликов по ключевым словам.

Сделано с использованием zipapp. Для нормальной работы надо запускать pyz.

## Запуск

```bash
wget https://github.com/hightemp/wapp_youtube_wrapper/releases/latest/download/wapp_youtube_wrapper.pyz
chmod a+x ./wapp_youtube_wrapper.pyz
./wapp_youtube_wrapper.pyz
```

## Упаковка

```bash
# https://docs.python.org/3/library/zipapp.html
python3 -m zipapp wapp_youtube_wrapper -p "/usr/bin/env python3"
```

![](screenshots/2022-12-25_10-06.png)
