# ------------------------------------------
# Name:     menu
# Purpose:  Menu interface (with GUI) for creating/managing tasks.
#
# Author:   Robin Siebler
# Created:  7/28/14
#------------------------------------------
__author__ = 'Robin Siebler'
__date__ = '7/28/14'

import util
from tasklist import Task, TaskList
from collections import OrderedDict
import sys
import ui                                        
import help
import speech

class TextDelegate(object):
    def textfield_did_change(self, textfield):
        view = textfield.superview
        button = view['button_select']
        button.enabled = textfield.text != ''

class Menu:
    def __init__(self):
        """Initialize the task list."""

        self.tasklist = TaskList()
        self.current_task = ''
        self.current_task_file = ''
        self.main_view = ''
        self.controls_enabled = False
        self.language = 'en-GB'
        self.speech_rate = 0.3

    def display_message(self, message):
        """Display any warnings or errors to the user."""

        self.message_dialog = ui.load_view('dialogs/message')
        self.message_dialog['label1'].text = message
        self.message_dialog.present('popover', popover_location=(500, 500))

    def show_tasks(self, sender, tasks=None):
        """Display the tasks (in ID order)

        :param tasks: tasks object
        """

        if not tasks:
            tasks = self.tasklist.tasks
        tv_text = ""
        if len(tasks) > 0:
            if not self.controls_enabled:
                #enable controls if there are tasks loaded
                self.main_view['button_number'].enabled = True
                self.main_view['button_priority'].enabled = True
                self.main_view['button_save'].enabled = True
                self.main_view['button_delete_task'].enabled = True
                self.main_view['button_modify'].enabled = True
                self.main_view['button_search'].enabled = True
                self.main_view['button_speak'].enabled = True
                self.controls_enabled = True
            for task in tasks:
                tv_text += '{}: {}\n\tPriority: {}\n\tTags: {}\n'.format(task.id, task.note, task.priority, task.tags)
        else:
            tv_text = '\nThere are no tasks to display!\n'

        self.task_textview.text = tv_text

    def show_tasks_by_priority(self, sender, tasks=None):
        """Display the tasks (in Priority order)

        :param tasks: tasks object
        """

        low_dict = OrderedDict()
        med_dict = OrderedDict()
        high_dict = OrderedDict()

        if not tasks:
            tasks = self.tasklist.tasks
        tv_text = ''

        if len(tasks) > 0:
            for task in tasks:
                if task.priority == 'Low':
                    low_dict[task.id] = [task.note, task.priority, task.tags]
                if task.priority == 'Medium':
                    med_dict[task.id] = [task.note, task.priority, task.tags]
                if task.priority == 'High':
                    high_dict[task.id] = [task.note, task.priority, task.tags]
        else:
            tv_text += '\nThere are no tasks to display!\n'
            return

        tv_text += 'High\n' + '-' * 20 + '\n'
        if len(high_dict) > 0:
            for key in high_dict:
                tv_text += '{}: {}\n\tTags: {}\n'.format(key, high_dict[key][0], high_dict[key][2])
        else:
            tv_text += 'There are no high priority tasks\n'

        tv_text += '\nMedium\n' + '-' * 20 + '\n'
        if len(med_dict) > 0:
            for key in med_dict:
                tv_text += '{}: {}\n\tTags: {}\n'.format(key, med_dict[key][0], med_dict[key][2])
        else:
            tv_text += 'There are no medium priority tasks\n'

        tv_text += '\nLow\n' + '-' * 20 + '\n'
        if len(low_dict) > 0:
            for key in low_dict:
                tv_text += '{}: {}\n\tTags: {}\n'.format(key, low_dict[key][0], low_dict[key][2])
        else:
            tv_text += 'There are no low priority tasks\n'

        self.task_textview.text = tv_text

    def prompt_search(self, sender):
        """Prompt the user for a search string."""

        if self.main_view['button_search'].title == "Show All":
            self.main_view['button_search'].title = "Search"
            self.show_tasks(None)
        else:
            self.search_dialog = ui.load_view('dialogs/search_tasks')
            self.search_dialog['textfield1'].begin_editing()
            self.search_dialog['textfield1'].action = self.search_tasks
            self.search_dialog.present('popover', popover_location=(500, 500))

    def search_tasks(self, sender):
        """Search the task list for a task whose note or tag contains the user provided search string."""

        search_string = self.search_dialog['textfield1'].text.lower()
        if search_string:
            tasks = self.tasklist.search(search_string)
            if tasks:
                self.search_dialog.close()
                self.main_view["button_search"].title = "Show All"
                self.show_tasks(sender, tasks=tasks)
            else:
                message = 'There were no tasks containing "{}".'.format(search_string)
                self.display_message(message)

    def prompt_add(self, sender):
        """Prompt the user to add a task."""

        self.add_dialog = ui.load_view('dialogs/add_task')
        self.add_dialog['textfield_task'].begin_editing()
        self.add_dialog.present('popover', popover_location=(500, 500))

    def add_task(self, sender):
        """Add a new task."""

        note = self.add_dialog['textfield_task'].text
        priority_num = self.add_dialog['segmentedcontrol1'].selected_index
        if priority_num == 0:
            priority = 'Low'
        elif priority_num == 1:
            priority = 'Medium'
        elif priority_num == 2:
            priority = 'High'
        tags = self.add_dialog['textfield_tags'].text
        self.tasklist.add_task(note, priority, tags)
        self.add_dialog.close()
        self.show_tasks(None)

    def prompt_delete_file(self, sender):
        """Prompt the user to delete a task file."""

        self.delete_dialog = ui.load_view('dialogs/delete_task_file')
        self.delete_dialog['textfield1'].begin_editing()
        self.delete_dialog.present('popover', popover_location=(500, 500))

    def delete_file(self, sender):
        """Delete a task file."""

        task_file = self.delete_dialog['textfield1'].text
        if not task_file == '':
            task_file = util.validate_file(task_file)
        if task_file:
            self.delete_dialog.close()
            util.delete(task_file)
        else:
            self.display_message(self.delete_dialog['textfield1'].text + ' is not a valid file!')
            self.delete_dialog['textfield1'].text = ''

    def prompt_delete_task(self, sender):
        """Prompt the user to delete a task."""

        self.delete_dialog = ui.load_view('dialogs/delete_task')
        self.delete_dialog['textfield1'].begin_editing()
        self.delete_dialog['textfield1'].action = self.delete_task
        self.delete_dialog.present('popover', popover_location=(500, 500))

    def delete_task(self, sendr):
        """Delete a task."""

        task_id = self.delete_dialog['textfield1'].text
        if task_id:
            task_id = self._validate_task_id(task_id)
            if task_id:
                self.delete_dialog.close()
                self.tasklist.delete_task(task_id)
                self.tasklist._renumber_tasks()
                self.show_tasks(None)
            else:
                self.delete_dialog['textfield1'].text = ''

    def prompt_modify_task_number(self, sender):
        """Prompt the user for the number of the task to modify."""

        self.modify_dialog = ui.load_view('dialogs/modify_task_number')
        self.modify_dialog['textfield1'].begin_editing()
        self.modify_dialog['textfield1'].action = self.modify_task
        self.modify_dialog.present('popover', popover_location=(500, 500))

    def modify_task(self, sender):
        """Change the fields of a task."""

        task_id = self._validate_task_id(self.modify_dialog['textfield1'].text)
        if task_id:
            self.current_task = self.tasklist._find_task(task_id)
            self.modify_dialog.close()
            self.modify_dialog = ui.load_view('dialogs/modify_task')
            self.modify_dialog['textfield_task'].text = self.current_task.note
            if self.current_task.priority == 'Low':
                self.modify_dialog['segmentedcontrol1'].selected_index = 0
            if self.current_task.priority == 'Medium':
                self.modify_dialog['segmentedcontrol1'].selected_index = 1
            if self.current_task.priority == 'High':
                self.modify_dialog['segmentedcontrol1'].selected_index = 2
            self.modify_dialog['textfield_tags'].text = self.current_task.tags
            self.modify_dialog.present('popover', popover_location=(500, 500))

    def save_modified_task(self, sender):
        """Save the contents of the modified task."""

        self.current_task.note = self.modify_dialog['textfield_task'].text
        priority_num = self.modify_dialog['segmentedcontrol1'].selected_index
        if priority_num == 0:
            self.current_task.priority = 'Low'
        elif priority_num == 1:
            self.current_task.priority = 'Medium'
        elif priority_num == 2:
            self.current_task.priority = 'High'
        self.current_task.tags = self.modify_dialog['textfield_tags'].text
        self.modify_dialog.close()
        self.show_tasks(None)

    def prompt_load(self, sender):
        """Prompt the user for the name of a task file."""

        self.load_dialog = ui.load_view('dialogs/load_task_file')
        self.load_dialog['textfield1'].begin_editing()
        self.load_dialog['textfield1'].action = self.load_tasks
        self.load_dialog.present('popover', popover_location=(500, 500))

    def load_tasks(self, sender):
        """Retrieve the contents of the task file."""

        task_file = self.load_dialog['textfield1'].text
        if task_file:
            task_file = util.validate_file(task_file)
            if task_file:
                self.load_dialog.close()
                self.tasklist.tasks = util.load(task_file)
                self.current_task_file = task_file
                Task.last_id = len(self.tasklist.tasks)
                self.show_tasks(None)
            else:
                self.display_message(self.load_dialog['textfield1'].text + ' is not a valid file')
                self.load_dialog['textfield1'].text = ''

    def prompt_save(self, sender):
        """Prompt the user for the name of a task file."""

        self.save_dialog = ui.load_view('dialogs/save_task_file')
        self.save_dialog['textfield1'].begin_editing()
        self.save_dialog['textfield1'].action = self.save_tasks
        self.save_dialog.present('popover', popover_location=(500, 500))

    def save_tasks(self, sender):
        """Save the tasks to the specified file."""

        task_file = self.save_dialog['textfield1'].text
        if task_file:
            if task_file.rfind('.tsk', len(task_file) - 4) == -1:
                task_file += '.tsk'
            self.save_dialog.close()
            if task_file == self.current_task_file:
                # some bug; even though the file should be closed, I can't overwrite it
                util.delete(task_file)
            util.save(self.tasklist.tasks, task_file)
        else:
            self.save_dialog['textfield1'].text = ''

    def prompt_speak(self, sender):
        """Prompt the user for the task(s) to speak."""

        self.prompt_dialog = ui.load_view('dialogs/speak_task_number')
        self.prompt_dialog['button_select'].enabled = False
        td = TextDelegate()
        self.prompt_dialog['textfield1'].delegate = td
        self.prompt_dialog["segmentedcontrol1"].action = self.display_speak_options
        self.prompt_dialog['textfield1'].begin_editing()
        self.prompt_dialog.present('popover', popover_location=(500, 500))

    def display_speak_options(self, sender):
        """Display the controls to enter a number"""

        if self.prompt_dialog["segmentedcontrol1"].selected_index == 0:
            self.prompt_dialog["label1"].hidden = False
            self.prompt_dialog["textfield1"].hidden = False
            if self.prompt_dialog["textfield1"].text == '':
                self.prompt_dialog['button_select'].enabled = False
            else:
                self.prompt_dialog["button_select"].enabled = True
        else:
            self.prompt_dialog["label1"].hidden = True
            self.prompt_dialog["textfield1"].hidden = True
            self.prompt_dialog['button_select'].enabled = True

    def enable_select(self, sender):
        """Enable the Select button after a task # has been provided."""

        self.prompt_dialog['button_select'].enabled = True
        self.main_view.set_needs_display()

    def process_speak_request(self, sender):
        """""Determine which task(s) to recite"""

        recite = self.prompt_dialog["segmentedcontrol1"].selected_index
        if recite == 0:
            task_id = self._validate_task_id(self.prompt_dialog['textfield1'].text)
            if task_id:
                self.prompt_dialog.close()
                self.current_task = self.tasklist._find_task(task_id)
                self.speak_task(self.current_task)
            else:
                self.prompt_dialog['textfield1'].text = ''
                self.prompt_dialog['button_select'].enabled = False
        else:
            self.prompt_dialog.close()
            for task in self.tasklist.tasks:
                self.speak_task(task)
        speech.say('Recitation complete', self.language, self.speech_rate)


    def speak_task(self, task):
        """""Recite the provided task"""

        speech.say("Task number " + str(task.id) + ", priority: " +
                   task.priority, self.language, self.speech_rate)
        speech.say(task.note, self.language, self.speech_rate)
        speech.say("This task has the following tags: ", self.language, self.speech_rate)
        tags = task.tags.split(" ")
        if len(tags) > 1:
            tags.insert(-1, "and")
        for tag in tags:
            speech.say(tag, self.language, self.speech_rate)

    def _validate_task_id(self, task_id):
        """Validate the given task ID.

        :return: False if an invalid ID was provided, otherwise a string containing the valid task id.
        """
        if task_id:
            if task_id.isdecimal() and int(task_id) <= len(self.tasklist.tasks):
                return task_id
            else:
                self.display_message('{} is not an existing task!'.format(task_id))
                return None

    def prompt_language(self, sender):
        """Prompt the user to select a language and speak rate."""

        # set languages
        ar = {'title': 'Arabic (Saudi Arabia)', 'code': 'ar-SA'}
        cs_CZ = {'title': 'Czech (Czech Republic)', 'code': 'cs-CZ'}
        da_DK = {'title': 'Danish (Denmark)', 'code': 'da-DK'}
        nl_BE = {'title': 'Dutch (Belgium)', 'code': 'nl-BE'}
        nl_NL = {'title': 'Dutch (Netherlands)', 'code': 'nl-NL'}
        en_AU = {'title': 'English (Australian)', 'code': 'en-AU'}
        en_IE = {'title': 'English (Ireland)', 'code': 'en-IE'}
        en_ZA = {'title': 'English (South Africa)', 'code': 'en-ZA'}
        en_GB = {'title': 'English (United Kingdom)', 'code': 'en-GB'}
        en_US = {'title': 'English (United States)', 'code': 'en-US'}
        fi_FI = {'title': 'Finnish (Finland)', 'code': 'fi-FI'}
        fr_CA = {'title': 'French (Canadian)', 'code': 'fr-CA'}
        fr_FR = {'title': 'French', 'code': 'fr-FR'}
        de_DE = {'title': 'German (Germany)', 'code': 'de-DE'}
        el_GR = {'title': 'Greek (Greece)', 'code': 'el-GR'}
        hi_IN = {'title': 'Hindi (India)', 'code': 'hi-IN'}
        hu_HU = {'title':'Hungarian (Hungary)', 'code': 'hu-HU'}
        id_ID = {'title': 'Indonesian (Indonesia)', 'code': 'id-ID'}
        it_IT = {'title': 'Italian (Italy)', 'code': 'it-IT'}
        ja_JP = {'title': 'Japanese (Japan)', 'code': 'ja-JP'}
        ko_KR = {'title': 'Korean (South Korea)', 'code': 'ko-KR'}
        no_NO = {'title': 'Norwegian (Norway)', 'code': 'no-NO'}
        pl_PL = {'title': 'Polish (Poland)', 'code': 'pl-PL'}
        pt_BR = {'title': 'Portuguese (Brazil)', 'code': 'pt-BR'}
        pt_PT = {'title': 'Portuguese (Portugal)', 'code': 'pt-PT'}
        ro_RO = {'title': 'Romanian (Romania)', 'code': 'ro-RO'}
        ru_RU = {'title': 'Russian (Russia)', 'code': 'ru-RU'}
        sk_SK = {'title': 'Slovak (Slovakia) ', 'code': 'sk-SK'}
        es_MX = {'title': 'Spanish (Mexico)', 'code': 'es-MX'}
        es_ES = {'title': 'Spanish (Spain)', 'code': 'es-ES'}
        sv_SE = {'title': 'Swedish (Sweden)', 'code': 'sv-SE'}
        th_TH = {'title': 'Thai (Thailand)', 'code': 'th-TH'}
        tr_TR = {'title': 'Turkish (Turkey)', 'code': 'tr-TR'}
        zh_CN = {'title': 'Chinese (China)', 'code': 'zh-CN'}
        zh_HK = {'title': 'Chinese (Hong Kong SAR China)', 'code': 'zh-HK'}
        zh_TW = {'title': 'Chinese (Taiwan)', 'code': 'zh-Tw'}
        self.lang_list = [ar, cs_CZ, da_DK, nl_BE, nl_NL, en_AU, en_IE, en_ZA, en_GB,
                     en_US, fi_FI, fr_CA, fr_FR, de_DE, el_GR, hi_IN, hu_HU, id_ID,
                     it_IT, ja_JP, ko_KR, no_NO, pl_PL, pt_BR, pt_PT, ro_RO, ru_RU,
                     sk_SK, es_MX, es_ES, sv_SE, th_TH, tr_TR, zh_CN, zh_HK, zh_TW
        ]

        self.prompt_lang = ui.load_view('dialogs/select_language')
        table = self.prompt_lang['tableview1']
        listsource = ui.ListDataSource(self.lang_list)
        table.data_source = listsource
        table.delegate = listsource
        listsource.action = self.set_language
        self.prompt_lang.present('sheet')

    def set_language(self, sender):
        """Set the language used for recitation based upon user selection."""

        self.language = self.lang_list[self.prompt_lang['tableview1'].selected_row[1]]['code']
        self.prompt_dialog['label_language'].text = self.lang_list[self.prompt_lang['tableview1'].selected_row[1]]['title']
        self.prompt_lang.close()

    def update_label(self, sender):
        """"Update the speech rate label as the slider value changes."""

        self.prompt_dialog['label_rate'].text = '{:.2f}'.format(self.prompt_dialog['slider1'].value)
        self.speech_rate = float(self.prompt_dialog['label_rate'].text)

    def run(self):

        main_view = ui.load_view("menu")
        # turn off invalid controls
        main_view['button_number'].enabled = False
        main_view['button_priority'].enabled = False
        main_view['button_save'].enabled = False
        main_view['button_delete_task'].enabled = False
        main_view['button_modify'].enabled = False
        main_view['button_search'].enabled = False
        main_view['button_speak'].enabled = False
        main_view.present("full_screen")
        self.main_view = main_view
        self.task_textview = main_view['task_textview']
        self.task_textview.text = help.help_text


if __name__ == '__main__':
    Menu().run()
