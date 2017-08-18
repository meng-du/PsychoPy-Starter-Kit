#!/usr/bin/env python

#
# A skeleton file for PsychoPy experiments
# Author: Meng Du
# August 2017
#

from psychopy_util import *
from config import *


def show_one_trial(images):
    # show instruction
    presenter.show_instructions(INSTR_TRIAL)
    # choose images randomly
    random_img_index_1 = random.randrange(len(images))
    random_img_index_2 = 1 - random_img_index_1  # this is the image that was not chosen in the above line
    # set image positions
    images[random_img_index_1].pos = presenter.LEFT_CENTRAL_POS
    images[random_img_index_2].pos = presenter.RIGHT_CENTRAL_POS
    # show images and get user response
    response = presenter.select_from_stimuli((images[random_img_index_1], images[random_img_index_2]),
                                             (random_img_index_1, random_img_index_2), RESPONSE_KEYS)
    return response


def validation(items):
    # check empty field
    for key in items.keys():
        if items[key] is None or len(items[key]) == 0:
            return False, str(key) + ' cannot be empty.'
    # check age
    try:
        if int(items['Age']) <= 0:
            raise ValueError
    except ValueError:
        return False, 'Age must be a positive integer'
    # everything is okay
    return True, ''


if __name__ == '__main__':
    # subject ID dialog
    sinfo = {'ID': '', 'Gender': ['Female', 'Male'], 'Age': '', 'Mode': ['Test', 'Exp']}
    show_form_dialog(sinfo, validation, order=['ID', 'Gender', 'Age', 'Mode'])
    sid = int(sinfo['ID'])

    # creater logging file
    infoLogger = logging.getLogger()
    if not os.path.isdir(LOG_FOLDER):
        os.mkdir(LOG_FOLDER)
    logging.basicConfig(filename=LOG_FOLDER + str(sid) + '.log', level=logging.INFO,
                        format='%(asctime)s %(levelname)8s %(message)s')
    # create data file
    dataLogger = DataHandler(DATA_FOLDER, str(sid) + '.txt')
    # save info from the dialog box
    dataLogger.write_data({
        k: str(sinfo[k]) for k in sinfo.keys()
    })
    # create window
    presenter = Presenter(fullscreen=(sinfo['Mode'] == 'Exp'))
    # load images
    images = presenter.load_all_images(IMG_FOLDER, '.png', img_prefix='img')
    random.shuffle(images)

    # show instructions
    presenter.show_instructions(INSTR_BEGIN)
    # show trials
    for t in range(NUM_TRIALS):
        data = show_one_trial(images)
        dataLogger.write_data({'trial_index': t, 'response': data})
    # end of experiment
    presenter.show_instructions(INSTR_END)
    infoLogger.info('End of experiment')
