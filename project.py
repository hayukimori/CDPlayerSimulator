#!/usr/bin/env python

# Baisc Libs
import os
import sys
import shutil
import argparse
from argparse import Namespace
from typing import Any
from pathlib import (Path, PosixPath)

# Audio Libs
import vlc
from resources.components import audio_scripts

# Engine Libs
from ursina.prefabs.health_bar import HealthBar
from ursina import (Ursina, Entity, Button,Func, Text, Audio, 
                    color, time, destroy, 
                    window, camera)


# Target Path where songs is located
APPLICATION_NAME: str = "PlayStar"
TARGET_PATH: str = ""

# Program's local path
__location__ = os.path.realpath(
    os.path.join(os.getcwd(), 
    os.path.dirname(__file__))
)


# Ursina Engine Definition
app = Ursina(
    title=APPLICATION_NAME,
    development_mode=False,
    borderless=False,
    fullscreen=False,
    window_type='onscreen',
    size=(896, 504)
)


def localpath(req_path: str) -> PosixPath:
    """Returns local path adding required path

    Args:
        req_path (str): A string path, example: "assets/textures/"

    Returns:
        PosixPath: Full path in PosixPath including required path (req_path)
    """

    rest_path = Path(os.path.join(__location__, req_path))
    return rest_path


def copy_cover_to_local(origin_path: PosixPath) -> list[str]:
    """Searches for cover file (image) and copies to local assets folder

    Args:
        origin_path (PosixPath): Location to search for image files

    Returns:
        list[str]: found matching files.
    """
    base_names: list[str] = ["cover", "folder"]
    extensions: list[str] = [".jpg", ".jpeg", ".png"]
    
    target_names: list[str] = [f"{name}{ext}" for name in base_names for ext in extensions]

    found_files: list = []

    for file in os.listdir(origin_path):
        if file.lower() in target_names:
            file_path: str = os.path.join(origin_path, file)
            found_files.append(file_path)

            if os.path.exists(x:=localpath('assets/textures/cover.jpg')):
                os.remove(x)
            
            shutil.copy2(src=file_path, dst=localpath("assets/textures/cover.jpg"))
            print(f"File {file} copied to {localpath("assets/textures/cover.jpg")}")

    print(found_files)
    return found_files


class LocalTempMemory():
    def __init__(self) -> None:
        """Local temporary memory
        """
        self.maindict = {}

class DirectoryManager():
    def __init__(self) -> None:
        """Manages files and directories
        """
        pass

    def getDirContent(self, path: PosixPath) -> dict[str, Any]:
        """Returns music files from path

        Args:
            path (PosixPath): Required path to list files

        Returns:
            dict[str, Any]: Found matching files and original path
        """
        content = os.listdir(path)
        content_filter = {
            "allowable": [".flac", ".mp3", ".m4a", ".ogg"]
        }

        if content:
            a_content = [x for x in content if x.endswith(tuple(content_filter["allowable"]))]
        else:
            a_content = []
        rest = { "path": path, "content": a_content if not None else [] }
        return rest


# Main UI
class Interface(Entity):
    def __init__(self, memory: LocalTempMemory):
        """The main UI where songs are showerd

        Args:
            memory (LocalTempMemory): class to store temporary data
        """

        super().__init__(self)

        # Main variables
        self.localmemory: LocalTempMemory = memory
        self.main_memory: dict = self.localmemory.maindict

        # Mangers
        self.dir_manager: DirectoryManager = self.main_memory["dir_manager"]
        self.soundmgr: audio_scripts.SoundManager = self.main_memory["sound_manager"]
        
        # Page-related variables
        self.main_memory["currentpage"] = 0
        self.buttons_buffer: list = []

        # Engine Defintions
        Text.default_resolution = 1080 * Text.size

        # Audio definitions
        self.dm = audio_scripts.DiscManager(localpath("assets/media/CD_SpinLoop.mp3"))

        # Album-art definitions
        current_album_image = Path(TARGET_PATH)
        tmp_copy = copy_cover_to_local(current_album_image)

        # Entities
        self.background: Entity = Entity(
            model="quad",
            color=color.white,
            texture="assets/textures/newgbg.jpg",
            scale_x= (16 / camera.aspect_ratio_getter()) * 2,
            scale_y= (9 / camera.aspect_ratio_getter()) * 2,
            z=1
        )

        self.cd_r: Entity = Entity(
            model="quad",
            color=color.white,
            texture="assets/textures/newcd.png",
            y=1,
            z=-.003,
            x=-3.6,
            scale = 4.5,
            scale_x= 5.6,
            rotation_x = 0,
        )
        

        self.dvd_logo: Entity = Entity(
            model="quad",
            color=color.white,
            texture="assets/textures/dvd_logo_white.png",
            scale_x=.8,
            scale_y=.5,
            z=-.01,
            y=3.7,
            x=5.8,
            visible=False
        )


        self.currentAlbumImage: Entity = Entity(
            model="quad",
            color=color.white,
            texture='cover.jpg',
            z=-.01,
            x = -4.2,
            y = 1,
            scale = 4.5,
        )


        self.top_logo: Text = Text(
            "PLAYSTAR",
            parent=self,
            color=color.white,
            font="assets/fonts/Good_Timing/good timing bd.otf",
            scale=15,
            position=(-6.5,3.9)
        )

        self.leftside: Entity = Entity(
            model="quad",
            color=color.white10,
            x=2.5,
            y=1,
            scale_x=7.5,
            scale_y=4.5,   
        )

        self.bottomside: Entity = Entity(
            model="quad",
            color=color.white10,
            y=-3,
            x=2.5,
            scale_x=7.5,
            scale_y=1
        )

        self.title_bottom_side: Entity = Entity(
            model="quad",
            color=color.white10,
            y=-2,
            x=2.5,
            scale_x=7.5,
            scale_y=.6
        )

        self.songTitle: Text = Text(
            "Song Title",
            parent=self,
            font="assets/fonts/NotoSansJP/static/NotoSansJP-Light.ttf",
            scale=10,
            x=-1,
            y=-1.9
        )

        self.songDescription: Text = Text(
            "Song Description",
            parent=self,
            font="assets/fonts/NotoSansJP/static/NotoSansJP-Light.ttf",
            scale=10,
            x=-1,
            y=-2.65
        )

        self.songTime: Text = Text(
            "00:00 / 00:00",
            parent=self,
            font="assets/fonts/NotoSansJP/static/NotoSansJP-Light.ttf",
            scale=10,
            x=-5,
            y=-1.5
        )

        self.progress_bar: HealthBar = HealthBar(
            parent=self,
            max_value=100, 
            animation_duration=.001,
            value=0,
            roundness=.20,
            show_text=False,
            show_lines=False,
            position=(-6.4, -3.7),
            scale=(12.6, .2)
        )

        self.volume_bar: HealthBar = HealthBar(
            parent=self,
            max_value=100,
            value=80,
            roundness=0,
            animation_duration=0,
            show_lines=False,
            show_text=False,
            scale=(.8, .3),
            color=color.white33,
            position=(-3,-1.4)
        )


        # UI Buttons
        self.play_btn: Button = Button(
            parent=self,
            texture="assets/textures/play_btn_white.png",
            color=color.white,
            scale_y=1.3,
            scale_x=1.5,
            x=-4.35,
            y=-2.6
        )

        self.skip_btn: Button = Button(
            parent=self,
            texture="assets/textures/skip_btn.png",
            color=color.white,
            scale=.8,
            x=-2.6,
            y=-2.62
        )

        self.prev_btn: Button = Button(
            parent=self,
            texture="assets/textures/prev_btn.png",
            color=color.white,
            scale=.8,
            x=-6,
            y=-2.63
        )
        
        self.nextpage_btn: Button = Button(
            parent=self,
            texture="assets/textures/arrow_right.png",
            color=color.white,
            scale = .5,
            scale_x = .4,
            x=6.6,
            y=1,
            enabled = False
        )


        self.prevpage_btn: Button = Button(
            parent=self,
            texture="assets/textures/arrow_left.png",
            color=color.white,
            scale = .5,
            scale_x = .4,
            x=-1.3,
            y=1,
            enabled = False
        )        



        # Logic setup
        if len(tmp_copy) <= 0:
            self.enable_nocover_mode()


        # Post Entity definitions
        self.volume_bar.texture = "assets/textures/volume_texture.png"
        self.volume_bar.bar.texture="assets/textures/volume_texture.png"
        self.volume_bar.bar.color=color.white33

        self.progress_bar.color=color.white10
        self.progress_bar.bar.color = color.white33

        # UI Buttons Setup
        self.nextpage_btn.on_click = Func(self.nextPage)
        self.prevpage_btn.on_click = Func(self.prevPage)
        self.prev_btn.on_click = Func(self.prevSong)
        self.skip_btn.on_click = Func(self.skipSong)

        ## Define button functions
        self.play_btn.on_click = self.play_clicked
        self.main_memory["songs_dir"] = Path(TARGET_PATH)
        self.main_memory["contentraw"] = self.dir_manager.getDirContent(
            self.main_memory["songs_dir"]
        )

        # Define update functions
        self.cd_r.update = self.update_cd_entity
        self.play_btn.update = self.update_play_btn

        # Run unction to create buttons based on folder contents
        self.render_dir(raw=self.main_memory["contentraw"])


    def enable_nocover_mode(self) -> None:
        """Disables dynamic album-art. Sets currentAlbumImage.texture to a defualt one
        """
        self.currentAlbumImage.texture = 'assets/textures/default_albumart.png'
    

    def play_clicked(self) -> None:
        """Manages what to do when 'play' button is pressed
        """

        vlc_state: vlc.State = vlc.State
        current_state: vlc.State = self.soundmgr.current_song.get_state()

        match current_state:
            case vlc_state.Paused:
                self.soundmgr.current_song.play()
            case vlc_state.Playing:
                self.soundmgr.current_song.pause()
            case _:
                return

            
    def nextPage(self) -> None:
        """Change's the current_page to the next one.
        """
        self.main_memory["currentpage"] += 1

        self.destroySonglist()
        self.render_dir(self.main_memory["contentraw"])
    
    def prevPage(self) -> None:
        """Change's the current_page to the previous one.
        """
        cpage = self.main_memory["currentpage"]

        if cpage > 0:
            self.main_memory["currentpage"] -= 1
            self.destroySonglist()
            self.render_dir(self.main_memory["contentraw"])

    def prevSong(self) -> None:
        """Change's the current song to the previous one
        """
        curr_song: str = self.soundmgr.current_song_name
        raw_path: PosixPath = self.main_memory["contentraw"]["path"]
        content: list = self.main_memory["contentraw"]["content"]

        if curr_song == None:
            return
        
        # Locate current song
        if cindex := content.index(curr_song) >= 0:
            self.soundmgr.playsong(
                str(
                    raw_path / content[cindex-1]
                ),
                content[cindex-1]
            )
            

    def skipSong(self) -> None:
        """Change's the current song to the next one
        """
        curr_song = self.soundmgr.current_song_name
        raw_path: PosixPath = self.main_memory["contentraw"]["path"]
        content = self.main_memory["contentraw"]["content"]
    
        if curr_song == None:
            return
        
        self.progress_bar.value = 0 # Resets progress bar

        # Locate current song
        cindex = content.index(curr_song)

        if cindex <= len(content):
            self.soundmgr.playsong(
                str(
                    raw_path / content[(
                        cindex+1 if cindex < len(content)-1 else 0
                    )]
                ),
                content[(
                    cindex+1 if cindex < len(content)-1 else 0
                )]
            )        

    def render_dir(self, raw: dict) -> None:
        """Gets the directory and render disponible songs as clickable buttons

        Args:
            raw (dict): takes DirectoryManager.getDirContent return format.
        """

        firstpath = raw["path"]
        content = raw["content"]
        current_page = self.main_memory["currentpage"]

        if len(content) > 5 and current_page == 0:
            self.nextpage_btn.enabled = True
        
        if current_page > 0:
            self.prevpage_btn.enabled = True
        else:
            self.prevpage_btn.enabled = False
        

        start = current_page * 5
        end = start + 5
        
        current_content = content[start:end]

        for i in range(5):
            try:

                # Verifies if file has title in metadata
                new_title = current_content[i]
                mt = audio_scripts.get_audio_metadata(
                    str(firstpath / current_content[i])
                )

                if mt != None:
                    if name := mt['title']:
                        new_title = name
                    else:
                        new_title = current_content[i]
                    
                # Verify title length to cut case it's too long
                if len(new_title) > 12:
                    new_title = new_title[:15] + '...'
                

                # Creates the button
                newb = Button(
                    parent=self, 
                    scale_y=.7, 
                    scale_x=7.5, 
                    text=f'{new_title}',
                    origin_y=-3.05, 
                    origin_x=-.33, 
                    y=.5-(i*.8), 
                    collider='box'
                )

                # Edit button's text config
                newb.text_entity.font = "assets/fonts/NotoSansJP/static/NotoSansJP-Light.ttf"
                newb.text_entity.wordwrap = 30
                newb.text_entity.line_height = .01
                newb.text_entity.scale = (1.4, 15)
                newb.text_entity.origin = (0, -50)
                
                # Edit button config and function
                newb.color = color.rgba(1, 1, 1, .01)
                newb.highlight_color = color.rgba(.149,.149,1, .4)
                newb._on_click = Func(
                    self.soundmgr.playsong, 
                    str(firstpath / current_content[i]),
                    current_content[i]
                )
                self.buttons_buffer.append(newb)

                
            except IndexError:
                # Disable the next_page button case it doesn't have enough files to a new page
                print(f"Index out of range: {i}")
                self.nextpage_btn.enabled = False
    
    
    def destroySonglist(self):
        """This function destroys the music selection buttons to render the next page
        """
        for btn in self.buttons_buffer:
            destroy(btn)

    def update_cd_entity(self):
        """Spinning CD Entity update
        """
        self.cd_r.rotation_z += 300 * time.dt
    

    def update_play_btn(self):
        """Updates play button
        """
        current_song_state: vlc.State = self.soundmgr.current_song.get_state()
        if current_song_state == vlc.State.Playing:
            self.play_btn.texture = "assets/textures/pause_btn.png"

        elif current_song_state == vlc.State.Paused:
            self.play_btn.texture = "assets/textures/play_btn_white.png"


    def update(self):
        """Ursina Update for the main Entity
        """
        
        # Updates volume bar
        self.volume_bar.value = (self.volume_bar.value * 0) + self.soundmgr.current_volume
        self.volume_bar.bar.texture_scale = (self.volume_bar.value/100, 1)

        # Updates the title and description labels
        self.songTitle.text = self.soundmgr.current_song_title
        self.songDescription.text = self.soundmgr.current_song_artist
        
        length = self.soundmgr.current_song.get_length()
        curr_time = self.soundmgr.current_song.get_time()

        if length != -1 and curr_time != -1:
            l_seconds = int((length)/1000 % 60)         # Remaining Seconds (ms to sec)
            l_minutes = int((length)/(1000*60)%60)      # Remaining Minutes (ms to min)
            
            ct_seconds = int((curr_time)/1000 % 60)     # Current Seconds   (ms to sec)
            ct_minutes = int((curr_time)/(1000*60)%60)  # Current Minutes   (ms to min)
            
            # Update songTime text (XX:XX / XX:XX)
            time_text = (
                f'{ct_minutes:02d}:{ct_seconds:02d}'
                '/'
                f'{l_minutes:02d}:{l_seconds:02d}'
            )

            self.songTime.text = time_text

            # Update progress bar
            try:
                self.progress_bar.value = (self.progress_bar.value * 0) \
                                          +(100 * curr_time) / length
            except ZeroDivisionError:
                pass
            
            # Verify if seconds and minutes are the same to skip song
            equals_minutes: bool = int(ct_minutes) == int(l_minutes)
            equals_seconds: bool = int(ct_seconds) == int(l_seconds)

            if equals_minutes and equals_seconds:
                if ct_minutes != 0 and ct_seconds != 0:
                    self.skipSong()


class LoadDiscInterface(Entity):
    def __init__(self, memory: LocalTempMemory) -> None:
        """'Loading' interface

        Args:
            memory (LocalTempMemory): main local memory class to store and read data
        """
        super().__init__()


        self.memory = memory

        self.background: Entity = Entity(
            parent=self,
            model="quad",
            color=color.white,
            texture="assets/textures/newgbg.jpg",
            scale_x= (16 / camera.aspect_ratio_getter()) * 2,
            scale_y= (9 / camera.aspect_ratio_getter()) * 2,
            z=1
        )

        self.dvd_logo: Entity = Entity(
            parent=self,
            model="quad",
            color=color.white,
            texture="assets/textures/DVD_logo.png",
            scale=(4, 2, 1),
        )

        self.loading_text_background: Entity = Entity(
            parent=self,
            model="quad",
            color=color.black,
            scale=(1.5, .5 ,1),
            position=(-6, 3.6)
        )
        self.loading_text: Text = Text(
            "Loading",
            font="assets/fonts/NotoSansJP/static/NotoSansJP-Bold.ttf",
            parent=self.loading_text_background,
            color=color.white,
            x=-.5,
            y=.2,
            scale=(10, 24),
            z=-.01
        )

        self.cd_load_audio: Audio  = Audio(
            'assets/media/CDSpin.mp3',
            volume=1,
            autoplay=False
        )

        self.cd_load_audio.play(start=0)
        self.cd_load_audio.update = self.update_loadaudio

        #print(self.loading_text.text)

    def callInterface(self, interface_class: Entity) -> None:
        """Calss any Interface class including only currenta

        Args:
            interface_class (Entity): an Interface class that takes only 'memory' as argument
        """
        self.destroy()
        interface_class(memory=self.memory)

    def destroy(self) -> None:
        """Destroys it's visual elements
        """
        destroy(self.background)
        destroy(self.dvd_logo)
        destroy(self.cd_load_audio)
        destroy(self.loading_text)
        destroy(self.loading_text_background)
        

    def update_loadaudio(self) -> None:
        """Updates cd_load_audio entity
        """
        if self.cd_load_audio.time >= 11.0:
            self.cd_load_audio.stop()
            self.callInterface(Interface)



class ApplicationBase:
    def __init__(self, applicationName: str) -> None:
        """Manages ursina configuration

        Args:
            applicationName (str): A name to this application
        """
        self.applicationName: str = applicationName
        self.WindowConfigs: dict[str, Func | Any] = {
            "e.fullscreen": Func(setattr, window, 'fullscreen', True),
            "d.fullscreen": Func(setattr, window, 'fullscreen', False),
            "e.vsync"     : Func(setattr, window, 'vsync', True),
            "d.vsync"     : Func(setattr, window, 'vsync', False),
        }

    def configWindow(self) -> None:
        """Window pre-config
        """
        self.WindowConfigs['d.fullscreen']()
        self.WindowConfigs['d.vsync']()

        window.color = color.black
        window.exit_button.visible = False
        window.fps_counter.enabled = True
        #window.title = self.applicationName
    

def main() -> None:
    """Main application run
    """

    # Define base and configure window
    appbase = ApplicationBase("DVD Player")
    appbase.configWindow()

    # Main vars
    temp_memory: LocalTempMemory = LocalTempMemory()
    dir_manager: DirectoryManager = DirectoryManager()
    soundmgr: audio_scripts.SoundManager = audio_scripts.SoundManager()

    # Arguments
    args = {
        "dir_manager": dir_manager,
        "local_memory": temp_memory,
        "sound_manager": soundmgr
    }

    temp_memory.maindict.update(args)

    # Launch interface
    LoadDiscInterface(memory=temp_memory)

    # Launch application
    app.run()


class ParserGen:
    def __init__(self):
        self.parser = argparse.ArgumentParser(
                        prog=APPLICATION_NAME,
                        description="A program to simulate DVD Readers"
        )

        self.parser.add_argument(
            'path', 
            type=str, 
            nargs='*', 
            help="The path for CD Files"
        )
    def print_help(self) -> None:
        self.parser.print_help()

    def parse_args(self, args: list[str]) -> Namespace:
        return self.parser.parse_args(args)

if __name__ == "__main__":
    main_parser = ParserGen()

    args = main_parser.parse_args(sys.argv[1:])

    if len(args.path) == 0:
        main_parser.print_help()
        sys.exit(1)
    else:
        TARGET_PATH = args.path[0]

    main()
