from tkinter import ttk
import tkinter as tk
from tkinter import filedialog
import os
from decimal import Decimal, InvalidOperation
from .constants import FieldTypes as FT
from sys import platform
from datetime import datetime
import csv
from .util import FileNameNotFoundException
from .util import RobotLogger

import matplotlib
# matplotlib.use('TkAgg')
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

class ValidateMixin:
    """Add a validation functionality to a widget"""

    def __init__(self, *args, error_var=None, **kwargs):
        self.error = error_var or tk.StringVar()
        super().__init__(*args, **kwargs)
        vcmd = self.register(self._validate)
        invcmd = self.register(self._invalid)

        self.config(
            validate='all',
            validatecommand=(vcmd, '%P', '%s', '%S', '%V', '%i', '%d'),
            invalidcommand=(invcmd, '%P', '%s', '%S', '%V', '%i', '%d')
        )

    def _toggle_error(self, on=False):
        self.config(foreground=('red' if on else 'black'))

    def _validate(self, proposed, current, char, event, index, action):
        self._toggle_error(False)
        self.error.set('')
        valid = True
        if event == 'focusout':
            valid = self._focusout_validation(event=event)
        elif event == 'key':
            valid = self._key_validation(proposed=proposed, current=current, char=char, index=index, action=action)
        if not valid:
            self._toggle_error(True)
        return valid

    def _focusout_validation(self, **kwargs):
        return True

    def _key_validation(self, **kwargs):
        return True

    def _invalid(self, proposed, current, char, event, index, action):
        if event == 'focusout':
            self._focusout_invalid(event=event)
        elif event == 'key':
            self._key_invalid(proposed=proposed, current=current, char=char, index=index, action=action)

    def _focusout_invalid(self, **kwargs):
        return True

    def _key_invalid(self, **kwargs):
        return True

    def trigger_focusout_validation(self):
        valid = self._validate('', '', '', 'focusout', '', '')
        if not valid:
            self._focusout_invalid(event='focusout')
        return valid


class ValidEntry(ValidateMixin, ttk.Entry):

    def _focusout_validation(self, **kwargs):
        valid = True
        if not self.get():
            valid = False
            self.error.set('A value is required')
        return valid


class ValidDateEntry(ValidateMixin, ttk.Entry):

    def _focusout_validation(self, **kwargs):
        valid = True
        if not self.get():
            valid = False
            self.error.set('A value is required')
        else:
            input_date = self.get()
            try:
                datetime.strptime(input_date, '%Y-%m-%d')
            except ValueError:
                self.error.set('Should be in yyyy-mm-dd')
                valid = False
        return valid


class ValidCombobox(ValidateMixin, ttk.Combobox):

    def _focusout_validation(self, **kwargs):
        valid = True
        if not self.get():
            valid = False
            self.error.set('A value is required')
        return valid


class ValidSpinbox(ValidateMixin, ttk.Spinbox):
    def __init__(self, *args, min_var=None, max_var=None, focus_update_var=None, from_='-Infinity', to='Infinity',
                 **kwargs):
        super().__init__(*args, from_=from_, to=to, **kwargs)
        self.resolution = Decimal(str(kwargs.get('increment', '1.0')))
        self.precision = (
            self.resolution.normalize().as_tuple().exponent)  # Just extracting exponent of the decimal so if it 1.2 then precision will be 2

        # there should always be a variable,
        # or some of our code will fail
        self.variable = kwargs.get('textvariable') or tk.DoubleVar()
        if min_var:
            self.min_var = min_var
            self.min_var.trace('w', self._set_minimum)
        if max_var:
            self.max_var = max_var
            self.max_var.trace('w', self._set_maximum)

        self.focus_update_var = focus_update_var
        self.bind('<FocusOut>', self._set_focus_update_var)

    def _set_focus_update_var(self, event):
        value = self.get()
        if self.focus_update_var and not self.error.get():
            self.focus_update_var.set(value)

    def _set_minimum(self, *args):
        current = self.get()
        try:
            new_min = self.min_var.get()
            self.config(from_=new_min)
        except (tk.TclError, ValueError):
            pass
        # if current value is empty then delete eveything else set the back the current value
        if not current:
            self.delete(0, tk.END)
        else:
            self.variable.set(current)

        self.trigger_focusout_validation()

    def _set_maximum(self, *args):
        current = self.get()
        try:
            new_max = self.max_var.get()
            self.config(to=new_max)
        except (tk.TclError, ValueError):
            pass
        # if current value is empty then delete eveything else set the back the current value
        if not current:
            self.delete(0, tk.END)
        else:
            self.variable.set(current)

        self.trigger_focusout_validation()

    def _key_validation(self, char, index, current, proposed, action, **kwargs):
        valid = True
        max_val = self.cget('to')

        if action == '0':
            return True
        if char not in ('0123456789'):
            return False
        proposed = Decimal(proposed)
        if proposed > max_val:
            return False
        return valid

    def _focusout_validation(self, **kwargs):
        valid = True
        min_value = self.cget('from')

        value = self.get()
        try:
            value = Decimal(value)
        except InvalidOperation:
            self.error.set('Invalid number string: {}'.format(value))
            return False
        if value < min_value:
            self.error.set('Value is too low(min{})'.format(min_value))
            return False
        max_val = self.cget('to')
        if value > max_val:
            self.error.set('Value is too High (max{})'.format(max_val))
            return False

        return valid


class LabelInput(tk.Frame):
    """A widget with Label and Input To-gather"""

    field_types = {
        FT.string: (ValidEntry, tk.StringVar),
        FT.string_list: (tk.Listbox, tk.StringVar),
        FT.long_string: (tk.Text, lambda: None),
        FT.decimal: (ValidSpinbox, tk.DoubleVar),
        FT.integer: (ValidSpinbox, tk.IntVar),
        FT.boolean: (ttk.Checkbutton, tk.BooleanVar)
    }

    def __init__(self, parent, label='', input_class=ttk.Entry, input_var=None, input_arg=None, label_args=None,
                 field_spec=None, **kwargs):
        super().__init__(parent, **kwargs)
        input_arg = input_arg or {}
        label_args = label_args or {}

        if field_spec:
            field_type = field_spec.get('type', FT.string)
            input_class = input_class or self.field_types(field_type)[0]
            var_type = self.field_types(field_type)[1]
            self.variable = input_var if input_var else var_type()
            # min max , increment
            if 'min' in field_spec and 'from_' not in input_arg:
                input_arg['from_'] = field_spec.get('min')
            if 'max' in field_spec and 'to' not in input_arg:
                input_arg['to'] = field_spec.get('max')
            if 'inc' in field_spec and 'increment' not in input_arg:
                input_arg['increment'] = field_spec.get('inc')
            # values
            if 'values' in field_spec and 'values' not in input_arg:
                input_arg['values'] = field_spec.get('values')
        else:
            self.variable = input_var
        """Setting the Variable for the Input Class as Button , Checkbox and radio buttons have different behavior"""
        if input_class in (ttk.Button, ttk.Combobox, ttk.Label, tk.LabelFrame):
            input_arg["text"] = label
            self.variable.set(label)
            input_arg["textvariable"] = self.variable
        elif input_class == tk.Listbox:
            input_arg["listvariable"] = self.variable

        elif input_class in (ttk.Radiobutton, ttk.Checkbutton):
            input_arg["text"] = label
            self.variable.set(label)
            input_arg["variable"] = self.variable
        else:
            self.label = ttk.Label(self, text=label, **label_args)
            self.label.grid(row=0, column=0, sticky=(tk.W + tk.E))
            input_arg["textvariable"] = self.variable

        """Creating the input Class"""
        self.input = input_class(self, **input_arg)
        self.input.grid(row=1, column=0, sticky=(tk.W + tk.E))
        self.columnconfigure(0, weight=1)
        if input_class not in (ttk.Button,):
            self.error = getattr(self.input, 'error', tk.StringVar())
            self.error.label = ttk.Label(self, textvariable=self.error, foreground='red')
            self.error.label.grid(row=2, column=0, sticky=(tk.W + tk.E))

    def grid(self, sticky=(tk.W + tk.E), **kwargs):
        super().grid(sticky=sticky, **kwargs)

    def bind(self, *args, **kwargs):
        self.input.bind(*args, **kwargs)

    """Defining Get Method for INPUT"""

    def get(self):
        try:
            if 'Listbox' in str(type(self.input)):
                return ";".join([self.input.get(item) for item in self.input.curselection()])
            elif self.variable:
                return self.variable.get()
            elif type(self.input) == tk.Text:
                self.input.get('1.0', tk.END)
            else:
                self.input.get()
        except (TypeError, tk.TclError):
            # when Numeric field Empty
            return ''

    def set(self, value, *args, **kwargs):
        if type(self.variable) == tk.BooleanVar:
            self.variable.set(bool(value))
        elif type(self.input) == ttk.Combobox:
            self.input['values'] = value
        elif self.variable:
            self.variable.set(value, *args, **kwargs)
        elif type(self.input) in (tk.Checkbutton, tk.Radiobutton):
            if value:
                self.input.select()
            else:
                self.input.deselect()
        elif type(self.input) == tk.Text:
            self.input.delete('1.0', tk.END)
            self.input.insert('1.0', value)
        else:  # input must be an Entry-type widget with no variable
            self.input.delete('0', tk.END)
            self.input.insert('0', value)

    """Defining Select Method for listBox"""

    def get_selected_values(self, *args, **kwargs):
        item_selected = ''
        for item in self.input.curselection():
            item_selected = "{}{}\n".format(item_selected, self.input.get(item))

        return item_selected.strip("\n")

    # def get_selected_values1(self,*args, **kwargs):
    #     return ";".join([ self.input.get(item) for item in self.input.curselection()])


class FolderTreeView(tk.Frame):
    def __init__(self, parent, path=None, sfilter=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.path = path
        self.logger = RobotLogger(__name__).logger
        self.entries = None
        self.sfilter = sfilter or []  # Adding the Filter
        # Creating the Tree
        self.tree = ttk.Treeview(self)

        # x-axis and y-axis scroll bars
        ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)

        # # Insert Root
        # iid = self.insert("", "end", os.path.basename(self.path))
        # self.entries[iid] = self.path
        # # Insert the Child
        # self.process_directory(iid, self.path)

        # add tree and scrollbars to frame
        self.tree.grid(in_=self, row=0, column=0, sticky="nsew")
        ysb.grid(in_=self, row=0, column=1, sticky="ns")
        xsb.grid(in_=self, row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.pack(side=tk.TOP, fill=tk.BOTH, expand=tk.Y)

    def sort(self, tv, col):
        itemlist = list(tv.get_children(''))
        itemlist.sort(key=lambda x: tv.set(x, col))
        for index, iid in enumerate(itemlist):
            tv.move(iid, tv.parent(iid), index)

    def insert(self, parent, index, path, name="", **kwargs):
        """
        add new element to TreeView
        """
        if "text" in kwargs:
            err = "arg 'text' not available"
            raise ValueError(err)
        kwargs["text"] = path
        if name:
            kwargs["text"] = name
        iid = self.tree.insert(parent, index, **kwargs)
        self.entries[iid] = path
        return iid

    def process_directory(self, parent, path, depth=5):
        if depth == 0:
            return
        for p in os.listdir(path):
            abspath = os.path.join(path, p)
            if os.path.isdir(abspath) and p not in self.sfilter:
                iid = self.insert(parent,
                                  'end',
                                  path=abspath,
                                  name=p,
                                  open=False)
                self.process_directory(iid, abspath, depth - 1)
            elif os.path.isfile(abspath) and '.robot' in p:
                self.insert(parent,
                            'end',
                            path=abspath,
                            name=p,
                            open=False)

    def update_tree(self, path, sfilter=None, **kwargs):
        self.path = os.path.abspath(path)
        self.entries = {"": self.path}

        self._remove_items()  # Remove Tree Items
        self.sfilter = sfilter or []  # Adding the Filter
        # Insert Root
        iid = self.insert("", "end", os.path.basename(self.path))
        self.entries[iid] = self.path
        # Insert the Child
        self.process_directory(iid, self.path)

    def _remove_items(self):
        items = self.tree.get_children()
        for item in items:
            self.tree.delete(item)

    def get_selected_item_path(self):
        iid = self.tree.focus()
        self.logger.debug(self.entries[iid])
        return self.entries[iid]

    def get(self):
        return self.get_selected_item_path()


class TabularTreeView(tk.Frame):
    def __init__(self, parent, columnNames=None, showCols='headings', selection_mode='extended', **kwargs):
        super().__init__(parent, **kwargs)
        self.entries = {"": ""}  # Empty Value
        self.columnNames = tuple(columnNames) or ()
        # Creating the Tree
        self.tree = ttk.Treeview(self, column=self.columnNames, show=showCols, selectmode=selection_mode, **kwargs)

        # x-axis and y-axis scroll bars
        ysb = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        xsb = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=ysb.set, xscroll=xsb.set)

        # Adding the Columns
        for col in self.columnNames:
            self.tree.heading(col, text=col)

        # add tree and scrollbars to frame
        self.tree.grid(in_=self, row=0, column=0, sticky=tk.NSEW)
        ysb.grid(in_=self, row=0, column=1, sticky="ns")
        xsb.grid(in_=self, row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.tree.bind("<Button-1>", self.on_click)
        # self.tree.bind("<Double-1>", self.on_double_click)

    def on_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "heading":
            self.sort(self.tree, self.columnNames[int(self.tree.identify('column', event.x, event.y).strip('#')) - 1])

    # def on_double_click(self, event):
    #     pass

    def sort(self, tv, col):
        itemlist = list(tv.get_children(''))
        itemlist.sort(key=lambda x: tv.set(x, col))
        for index, iid in enumerate(itemlist):
            tv.move(iid, tv.parent(iid), index)

    def get_items(self):
        return [self.entries[id] for id in self.entries.keys()
                if id != '']

    def get_selected_items(self):
        selected_item = [self.entries[id] for id in self.tree.selection()]
        return selected_item

    def get(self):
        return self.get_selected_items()

    def delete_selected_item(self):
        items = self.tree.selection()
        if len(items) > 0:
            for item in items:
                self.tree.delete(item)
                del self.entries[item]

    def set_column_width(self, col_name, i_width):
        if col_name in self.columnNames:
            self.tree.column(col_name, width=i_width)

    def insert_item(self, test_case, allow_duplicates=True, **kwargs):
        if not allow_duplicates:
            if not self._is_exiting_node(test_case):
                self._add_node(test_case, **kwargs)
        else:
            self._add_node(test_case, **kwargs)

    def _is_exiting_node(self, test_case):
        return test_case in self.entries.values()

    def _add_node(self, test_case, **kwargs):
        if 'values' in kwargs:
            iid = self.tree.insert("", "end", **kwargs)
            self.entries[iid] = test_case

    def clear_items(self):
        for child in self.tree.get_children():
            self.tree.delete(child)
        self.entries = {"": ""}

    def grid(self, sticky=(tk.W + tk.E), **kwargs):
        super().grid(sticky=sticky, **kwargs)

    def to_csv(self):
        file_type =(("CSV Files",'*.csv'),)
        file_name = filedialog.asksaveasfilename(confirmoverwrite=True, title='Save As...',defaultextension='.csv',
                                                 filetypes=file_type)
        if file_name:
            try:
                with open(file_name, 'w') as f:
                    writer = csv.writer(f)
                    writer.writerow(self.columnNames)
                    for child in self.tree.get_children():
                        writer.writerow(self.tree.item(child)['values'])
            except PermissionError as e:
                raise e
        else:
            raise FileNameNotFoundException('Empty File Name.')


class ContextItemMix:
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.cMenu = tk.Menu(parent, tearoff=0)

    def _rerun(self):
        print("rerun")
        pass

    def open(self):
        print("Open")
        pass

    def update(self):
        print("Update")
        pass

    def add_cmd(self, **kwargs):
        self.cMenu.add_command(**kwargs)


class BatchTabularTreeView(ContextItemMix, TabularTreeView):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        if platform == 'darwin':
            self.tree.bind("<Button-2>", self.do_popup)
        else:
            self.tree.bind("<Button-3>", self.do_popup)

    def do_popup(self, event):
        # display the popup menu
        try:
            self.cMenu.selection = self.tree.identify_row(event.y)
            # print("selection", self.cMenu.selection)
            self.cMenu.post(event.x_root, event.y_root)
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            self.cMenu.grab_release()


class ScriptTabularTreeView(ContextItemMix, TabularTreeView):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        if platform == 'darwin':
            self.tree.bind("<Button-2>", self.do_popup)
        else:
            self.tree.bind("<Button-3>", self.do_popup)

    def do_popup(self, event):
        # display the popup menu
        try:
            self.cMenu.selection = self.tree.identify_row(event.y)
            # print("selection", self.cMenu.selection)
            self.cMenu.post(event.x_root, event.y_root)
        finally:
            # make sure to release the grab (Tk 8.0a1 only)
            self.cMenu.grab_release()


class BarGraph(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=parent)
        self.toolbar = NavigationToolbar2Tk(self.canvas, parent)
        self.toolbar.pack_forget()

    def set_axis_label(self, x_axis, y_axis, title):
        self.axes.set_xlabel(x_axis)
        self.axes.set_ylabel(y_axis)
        self.axes.set_title(title)

    def add_bar(self, **kwargs):
        self.axes.bar(**kwargs)
        self.axes.legend()
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.toolbar.pack()



