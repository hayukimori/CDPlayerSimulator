import vlc 
import time

player: vlc.Instance = vlc.Instance()
media_list: vlc.MediaList = player.media_list_new()
media_player: vlc.MediaListPlayer = player.media_list_player_new()

media = player.media_new("/home/hayukimori/Músicas/2018.12.30 [K2-0018] COMPACT DISC [C95]/岸田教団&THE明星ロケッツ - COMPACT DISC.flac")

media_list.add_media(media)

media_player.set_media_list(media_list)
media_player.play()

print(media_list)
time.sleep(10)