# Copyright 2013 Rooter Analysis S.L.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from os import listdir, remove
from os.path import abspath, dirname

from django.core.management.base import BaseCommand, CommandError

from moocng.courses.models import Question


class Command(BaseCommand):

    help = "Remove all the unused last frames from the server."

    def get_image_name(self, q):

        """
        Get the image file name for the specified question.

        frame: get full path of the image
        frame_img: get the image file name
        frame_id: get the id, removing any file extension
        """
        frame = self.q.last_frame.path
        frame_img = frame.split('/')[-1]
        #frame_id = frame_img.split('.')[0]
        return frame_img

    def delete_all_images(self):

        """
        This method deletes all the unused images. It creates an empty list for
        the valid files that populates with the current filenames located in the
        Question.last_frame field. After that it removes them from the full file
        list of the question media directory.

        all_questions: List all the questions in the platform
        valid_images: Images currently in use
        image_path: Full path for the questions media directory
        all_images: List containing all the images in the media image directory.
                    We get the first question and assume all the others have the
                    same directory.
        """
        self.stdout.write(" * Getting all the question objects...\n")
        try:
            all_questions = Question.objects.all()
            image_path = abspath(dirname(all_questions[0].last_frame.path))
            valid_images = []
            all_images = listdir(image_path)
            try:
                self.stdout.write(" * Cleaning unused image files (this may take a while)...\n")
                try:
                    for self.q in all_questions:
                        img_name = self.get_image_name(self.q)
                        valid_images.append(img_name)
                except:
                    raise CommandError("Couln't obtain the image filenames.\n")
                try:
                    for img in valid_images:
                        all_images.remove(img)
                except:
                    raise CommandError("Couldn't generate the file list for removal.\n")
                try:
                    for img in all_images:
                        remove(image_path + '/' + img)
                    self.stdout.write("\n \033[1;42m* Successfully deleted all unused images.\033[1;m\n\n")
                except:
                    raise CommandError("Couldn't remove files from disk.\n")
            except:
                raise CommandError("Couln't delete files.\n")
        except:
            raise CommandError("Couldn't grab Question objects.\n")

    def handle(self, *args, **options):
        self.stdout.write("\n * Starting removal of images...\n")
        self.delete_all_images()
