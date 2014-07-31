#------------------------------------------
# Name:     menu
# Purpose:  Menu interface for creating/managing tasks.
#
# Author:   Robin Siebler
# Created:  7/14/13
#------------------------------------------
__author__ = 'Robin Siebler'
__date__ = '7/14/13'

import util
from tasklist import Task, TaskList
from collections import OrderedDict
import sys

class Menu:

    def __init__(self):
        """Initialize the task list and populate the dictionary for menu actions."""

        self.tasklist = TaskList()
        self.choices = {'1': self.load_tasks,
                        '2': self.save_tasks,
                        '3': self.show_tasks,
                        '4': self.show_tasks_by_priority,
                        '5': self.search_tasks,
                        '6': self.add_task,
                        '7': self.delete_task,
                        '8': self.modify_task,
                        '9': self.show_menu,
                        '10': self.quit
        }

    def show_menu(self):
        """Display the menu."""
        print("""

        Task List Menu:

        1.  Load Tasks
        2.  Save Tasks
        3.  Show Tasks by Number
        4.  Show Tasks by Priority
        5.  Search Tasks
        6.  Add Task
        7.  Delete Task
        8.  Modify Task
        9.  Display this menu
        10. Quit
        """)

    def show_tasks(self, tasks=None):
        """Display the tasks (in ID order)

        :param tasks: tasks object
        """

        if not tasks:
            tasks = self.tasklist.tasks

        if len(tasks) > 0:
            print('\nTasks:\n')
            for task in tasks:
                print('{}: {}\n\tPriority: {}\n\tTags: {}'.format(task.id, task.note, task.priority, task.tags))
        else:
            print('\nThere are no tasks to display!\n')

    def show_tasks_by_priority(self, tasks=None):
        """Display the tasks (in Priority order)

        :param tasks: tasks object
        """

        low_dict = OrderedDict()
        med_dict = OrderedDict()
        high_dict = OrderedDict()

        if not tasks:
            tasks = self.tasklist.tasks

        if len(tasks) > 0:
            print('\nTasks:\n')
            for task in tasks:
                if task.priority == 'Low':
                    low_dict[task.id] = [task.note, task.priority, task.tags]
                if task.priority == 'Medium':
                    med_dict[task.id] = [task.note, task.priority, task.tags]
                if task.priority == 'High':
                    high_dict[task.id] = [task.note, task.priority, task.tags]
        else:
            print('\nThere are no tasks to display!\n')
            return

        print('High\n' + '-' * 20)
        if len(high_dict) > 0:
            for key in high_dict:
                print('{}: {}\n\tTags: {}\n'.format(key, high_dict[key][0], high_dict[key][2]))
        else:
            print('There are no high priority tasks\n')

        print('Medium\n' + '-' * 20)
        if len(med_dict) > 0:
            for key in med_dict:
                print('{}: {}\n\tTags: {}\n'.format(key, med_dict[key][0], med_dict[key][2]))
        else:
            print('There are no medium priority tasks\n')

        print('Low\n' + '-' * 20)
        if len(low_dict) > 0:
            for key in low_dict:
                print('{}: {}\n\tTags: {}\n'.format(key, low_dict[key][0], low_dict[key][2]))
        else:
            print('There are no low priority tasks!\n')

    def search_tasks(self):
        """Search the task list for a task whose note or tag contains the user provided search string."""

        search_string = raw_input('Enter the tet you wish to search for: ').lower()
        tasks = self.tasklist.search(search_string)
        if tasks:
            self.show_tasks(tasks)
        else:
            print('\nThere were no tasks containing "{}".\n'.format(search_string))

    def add_task(self):
        """Add a new task."""

        note = raw_input('Enter a task: ')
        priority = self._get_priority()
        tags = raw_input('Enter the tag(s) for your task: ')
        self.tasklist.add_task(note, priority, tags)

    def delete_task(self):
        """Delete a task."""

        task_id = self._validate_task_id('delete: ')
        if task_id:
            self.tasklist.delete_task(task_id)
            self.tasklist._renumber_tasks()
            print('The task was deleted.')

    def modify_task(self):
        """Change one of the fields of a task. The user is prompted with the available choices."""

        task_id = self._validate_task_id('modify: ')
        if task_id:
            choice = None
            while not choice:
                choice = raw_input('What do you wish to modify? (T)ask, (P)riority or T(a)gs: ').title()
                if choice not in ['T', 'P', 'A'] and choice not in ['Task', 'Priority', 'Tags']:
                    print ('{} is not a valid choice.'.format(choice))
                    choice = None

            task = self.tasklist._find_task(task_id)
            if choice is 'T' or choice is 'Task':
                task.note = raw_input('Enter a task: ')
            elif choice is 'P' or choice is 'Priority':
                task.priority = self._get_priority()
            elif choice is 'A' or choice is 'Tags':
                task.tags = raw_input('Enter the tag(s) for your task: ')

    def run(self):
        """Display the menu and invoke the desired action."""

        self.show_menu()
        while True:
            choice = raw_input('\nEnter an option ("9" will re-display the menu): ')
            action = self.choices.get(choice)
            if action:
                action()
            else:
                print('\n{} is not a valid option!\n'.format(choice))

    def quit(self):
        """Exit the app."""

        sys.exit(0)

    def load_tasks(self):
        """Prompt the user for a file name and then capture the contents of the file."""

        task_file = raw_input('Enter the name of the file containing your tasks (".tsk will be added"): ')
        if task_file.rfind('.tsk', len(task_file) -4) == -1:
            task_file += '.tsk'
        self.tasklist.tasks = util.load(task_file)
        Task.last_id = len(self.tasklist.tasks)

    def save_tasks(self):
        """Prompt the user for a file name and then save the tasks to that file."""

        task_file = raw_input('Enter a file name for saving your tasks in (".tsk" will be the added): ')
        if task_file.rfind('.tsk', len(task_file) -4) == -1:
            task_file += '.tsk'
        util.save(self.tasklist.tasks, task_file)

    def _get_priority(self):
        """Prompt the user for a priority for a task.

        :return: string containing a valid priority
        """

        priority = None
        while not priority:
            priority = raw_input('Enter a priority for the task - (valid options are (L)ow, (M)edium and (H)igh: ').title()
            if priority not in ['L', 'M', 'H'] and priority not in ['Low', 'Medium', 'High']:
                print('{} is not a valid option'.format(priority))
                priority = None

        if priority == 'L': priority = 'Low'
        elif priority == 'M': priority = 'Medium'
        elif priority == 'H': priority = 'High'

        return priority

    def _validate_task_id(self, prompt):
        """Prompt the user for a task ID and validate it.

        :param prompt: string appended to user prompt indicating the action to be taken after validation.
        :return: False if an invalid ID was provided, otherwise a string containing the valid task id.
        """

        task_id = raw_input('Enter the Number of the Task you wish to ' + prompt)
        if task_id.isdecimal() and int(task_id) <= len(self.tasklist.tasks):
            return task_id
        else:
            print('{} is not an existing task!'.format(task_id))
            return None

if __name__ == '__main__':
    Menu().run()
