from factories import get_factory_class_by_name

from arguments_parsing import get_arguments
from coordinators import get_coordinator_class_by_name
from video_creation import create_video

if __name__ == '__main__':
    arguments = get_arguments()

    content_factory_class = get_factory_class_by_name(
            arguments['factory'] if not arguments['stdin'] else 'StdInput'
        )
    video_coordinator_class = get_coordinator_class_by_name(arguments['coordinator'])

    create_video(video_coordinator_class, content_factory_class, arguments)