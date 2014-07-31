#------------------------------------------
# Name:     util
# Purpose:  Utility functions for other scripts
#
# Author:   Robin Siebler
# Created:  7/17/13
#------------------------------------------
__author__ = 'Robin Siebler'
__date__ = '7/17/13'

import os, pickle


def delete(task_file):
	"""Delete the task file specified by the user.
	
	:param task_file: a previously created task file
	"""
	
	os.remove(task_file)

def load(pickle_file):
    """Loads a file that has been pickled and reads its contents.

    :param pickle_file: the file that has been pickled
    :return: The object in the file, or None if an error occurs
    """

    if os.path.exists(pickle_file):
        try:
            with open(pickle_file, 'rb') as fh:
                obj = pickle.load(fh)
                return obj
        except IOError as e:
            print(str(e))
            return None
        except pickle.PickleError as e:
            print(str(e))
            return None
    else:
        print('The file {} does not exist!'.format(pickle_file))

def save(obj, pickle_file):
    """Save an object into a pickle file.

    :param obj: The object to pickle
    :param pickle_file: The name of the file to create.
    """

    try:
        with open(pickle_file, 'wb') as fh:
            pickle.dump(obj, fh)
    except IOError as e:
        print(str(e))
    except pickle.PickleError as e:
        print(str(e))

def validate_file(task_file):
	"""Verify that the specified file exists.
	
	:param task_file: The file name provided by the user.
	"""
	if task_file.rfind('.tsk', len(task_file) -4) == -1:
		task_file += '.tsk'
	if os.path.exists(task_file):
		return task_file
	else:
		return None	
	
if __name__ == '__main__':
    pass  # put call to unit tests here?
