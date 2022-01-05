#!/usr/bin/env python

#
# An example experiment using psychopy utilities
# Author: Meng Du
# August 2017
#

from psychopy_util import *
from config import *
import random


def show_one_trial(images, presenter):
    # show instruction
    presenter.show_instructions(INSTR_TRIAL)
    # choose images randomly
    random_img_index_1 = random.randrange(len(images))
    random_img_index_2 = 1 - random_img_index_1  # the other image that was not randomly chosen in the above line
    # set image positions
    images[random_img_index_1].pos = presenter.LEFT_CENTRAL_POS
    images[random_img_index_2].pos = presenter.RIGHT_CENTRAL_POS
    # show images and get user response
    stimuli = (images[random_img_index_1], images[random_img_index_2])
    response = presenter.select_from_stimuli(stimuli, RESPONSE_KEYS)
    response['selected_img'] = stimuli[response['selection']]._imName
    return response


def validation(items):
    # check for empty fields
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


def main():
    # subject ID dialog
    sinfo = {'ID': '', 'Gender': ['Female', 'Male'], 'Age': '', 'Screen': ['Test', 'Exp']}
    show_form_dialog(sinfo, validation, order=['ID', 'Gender', 'Age', 'Screen'])
    sid = int(sinfo['ID'])

    # create logging file
    infoLogger = DataLogger(LOG_FOLDER, str(sid) + '.log', 'info_logger', logging_info=True)
    # create data file
    dataLogger = DataLogger(DATA_FOLDER, str(sid) + '.txt', 'data_logger')
    # save info from the dialog box
    dataLogger.write_json({
        k: str(sinfo[k]) for k in sinfo.keys()
    })
    # create window
    presenter = Presenter(fullscreen=(sinfo['Screen'] == 'Exp'), info_logger='info_logger')
    # load images
    images = presenter.load_all_images(IMG_FOLDER, '.png', img_prefix='img')
    random.shuffle(images)

    # show instructions
    presenter.show_instructions(INSTR_BEGIN)
    # show trials
    for t in range(NUM_TRIALS):
        data = show_one_trial(images, presenter)
        infoLogger.logger.info('Writing to data file')
        dataLogger.write_json({'trial_index': t, 'response': data})
    # end of experiment
    presenter.show_instructions(INSTR_END)
    infoLogger.logger.info('End of experiment')

if __name__ == '__main__':
    main()
