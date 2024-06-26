from moviepy.editor import ColorClip, ImageClip, CompositeVideoClip, TextClip, AudioFileClip, CompositeAudioClip, concatenate_audioclips
from icrawler.builtin import GoogleImageCrawler
import json, random, os

from effects import zoom_in_effect
from media_generators.GoogleImagesFetcher import GoogleImagesFetcher
from uuid import uuid4
from config import ROOT_DIR
import re

# Coordinator for Youtube Shorts compatible
# videos that consist of six "slides" with
# white text and a zooming background image
class SixFactsVideoCoordinator:
    
    standardGPTPrompt = """Generate a JSON array containing 6 detailed slides on "{{SUBJECT}}". 

                        Each slide should have a title (up to 5 words) in the 'title' key and a descriptive sentence (without quotes) in the 'content' key.

                        Additionally, include a concise, contextually relevant image description in the 'image' key for each slide.

                        Important!!! Provide only the raw/pure JSON object as plain text, in such a way that it's possible to parse it directly from your response, so don't include any additional text or marks other than the JSON object.

                        Your answer must be a valid JSON object, such that I can parse it without any errors. So, no explanation and no comments, just and only the JSON object. Like this:

                        [ {
                            "title": "...",
                            "content": "...",
                            "image": "..."
                        }, ... ]"""
    
    def __init__(self, theme, content, title_font, content_font, image_generator = GoogleImagesFetcher()):
        self.theme = theme
        self.content = json.loads(content)
        self.title_font = title_font
        self.content_font = content_font
        self.image_generator = image_generator

    def make_background(self, video_maker):
        # background = ColorClip((video_maker.width, video_maker.height), (0,0,0)).set_duration(59)
        background_list = []
        for i, f in enumerate(self.content):
            image = self.image_generator.generate(f['image'])
            image = image.resize(width=video_maker.width) if image.h > image.w else image.resize(height=video_maker.height)
            
            path = os.path.join(ROOT_DIR, "tmp_audio", str(uuid4()) + ".wav")
            print('element: ', f)
            script = re.sub(r'[^\w\s.?!]', '', f['content'])
            video_maker.tts.synthesize(script, path)
            print("=> Wrote TTS to " + path)
            tts_clip = AudioFileClip(path)
            # .set_fps(44100).set_duration(9.8).set_start(i*9.8).set_end((i+1)*9.8)
            # image = image.set_audio(tts_clip)

            image = zoom_in_effect(image.set_duration(9.8).set_audio(tts_clip)\
                        .set_start(i*9.8)\
                        .set_pos(("center", "center")))
            background_list.append(image)
            # background = CompositeVideoClip([background, image])
        
        # background = CompositeVideoClip([
        #                 background,
        #                 ColorClip((video_maker.width, video_maker.height), (0,0,0))\
        #                     .set_opacity(0.8)\
        #                     .set_duration(59)
        #                 ])
        background = CompositeVideoClip(background_list)
        return [background]
    
    def make_content(self, video_maker):
        slides = []
        for i, element in enumerate(self.content):
            title = TextClip(element['title'], 
                             fontsize=25, 
                             font=self.title_font, 
                             method='label', 
                             color='white')\
                    .set_duration(9.8)\
                    .set_start(i*9.8)\
                    .set_end((i+1)*9.8)\
                    .margin(top=50, opacity=0)\
                    .set_pos(("center", "top"))
            
            text = TextClip(element['content'], 
                            fontsize=37, 
                            font=self.content_font, 
                            method='caption', 
                            color='white', 
                            size=(video_maker.width - 100, 512), 
                            align='West')\
                    .margin(bottom=50, opacity=0)\
                    .set_duration(9.8)\
                    .set_start(i*9.8)\
                    .crossfadein(1)\
                    .set_end((i+1)*9.8)\
                    .set_pos(("center", "bottom"))
            
            timer = ColorClip((video_maker.width, video_maker.height), (255, 0, 0))\
                    .resize(lambda t: (10 + (video_maker.width - 10)*(t/9.8), 10))\
                    .set_duration(9.8)\
                    .set_start(i*9.8)\
                    .set_pos(("center", "top"))
            
            slides.extend([title, text, timer])

        return slides

    def make_watermark(self, video_maker):
        return []

    def make_audio(self, video_maker):
        tts_list = []
        print('inside make_audio')
        print('self content: ', self.content)
        for i, element in enumerate(self.content):
            path = os.path.join(ROOT_DIR, "tmp_audio", str(uuid4()) + ".wav")
            print('element: ', element)
            script = re.sub(r'[^\w\s.?!]', '', element['content'])

            video_maker.tts.synthesize(script, path)
            
            print("=> Wrote TTS to " + path)
            tts_clip = AudioFileClip(path).set_fps(44100).set_duration(9.8).set_start(i*9.8).set_end((i+1)*9.8)
            tts_list.append(tts_clip)
        # comp_audio = CompositeAudioClip(tts_list)
        # path = os.path.join(ROOT_DIR, "result" + ".wav")
        # comp_audio.write_audiofile(path)
        # return []


        return [concatenate_audioclips(tts_list)]

        # return tts_list
        # return [concatenate_audioclips(tts_list)]
        # comp_audio = CompositeAudioClip(tts_list)
        # path = os.path.join(ROOT_DIR, "tmp_audio", str(uuid4()) + ".wav")
        # # comp_audio.write_audiofile(path)
        # print("=> comp_audio finished")
        # return [comp_audio]