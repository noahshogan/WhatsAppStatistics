#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import datetime

import matplotlib.pyplot as plt
from bokeh.models import pd
from tkFileDialog import askopenfilename
from Tkinter import *
import tkMessageBox
from dateutil.parser import parse

delimiter = None


# ~~~~ FUNCTIONS~~~~

def open_file():
    global file_path
    file_path = askopenfilename(title="Choose data file", filetypes=[('Whatsapp txt history file', '.txt'), ])
    path_entry.delete(0, END)
    path_entry.insert(0, file_path)


def dialog(text, message_type):
    if message_type == "info":
        tkMessageBox.showinfo(title="", message=text, parent=root, type=tkMessageBox.OK)
    if message_type == "error":
        tkMessageBox.showerror(title="", message=text, parent=root, type=tkMessageBox.OK)


def get_name_and_date(line):
    name = None
    date = None
    try:
        a = line.split(' ')
        if radio_var.get() == 1:
            date = a[0]
        else:
            date = a[0].split('[')[1]
        # In case the name is not save in contacts and it's represented as a number
        if a[4].__contains__('+'):
            name = a[4] + a[5]
        else:
            # In case the name is saved in contacts
            name = line.split(delimiter)[1].split(':')[0]
    except Exception as e:
        x = e
    return name, date


def get_radio_var_delimiter():
    global delimiter
    if radio_var.get() == 1:
        delimiter = '-'
    if radio_var.get() == 2:
        delimiter = ']'


def parse_txt_file():
    txt_file_path = path_entry.get()
    try:

        # Validate input
        if len(txt_file_path) == 0:
            raise Exception("txt file path is empty, please select file")

        # Open fle
        lines = codecs.open(txt_file_path, encoding='utf-8')
        dic = dict()
        last_days_filter = False
        today = None
        margin = None
        get_radio_var_delimiter()
        if number_of_days.get() != '' or len(number_of_days.get()) > 0:
            last_days_filter = True
            today = datetime.date.today()
            margin = datetime.timedelta(days=int(number_of_days.get()))

        # Parse each line to get the message owner name
        for line in lines:
            if line.__contains__('האבטחה'.decode('UTF-8')) or line.lower().__contains__('security'):
                continue
            try:
                name, i_date = get_name_and_date(line)
                if name is None:
                    continue
                date = parse(i_date)
                if last_days_filter:
                    if today >= datetime.date(date.year, date.month, date.day) >= today - margin:
                        dic[name] = dic.get(name, 0) + 1
                if not last_days_filter:
                    dic[name] = dic.get(name, 0) + 1
            except Exception as e:
                x = 1
        # Move all the data into list of tuples
        tuples = []
        for name, count in dic.iteritems():
            if count > 1:
                tuples.append((name, count))

        # Sort the list
        tuples.sort(key=lambda xx: xx[1])

        # Create two list for the plot X and Y bars
        names = []
        counts = []
        for x in tuples:
            name = x[0]
            count = x[1]
            print x[0], ':', x[1]
            # In case the name is in hebrew we should reverse it for the printing
            if any(u"\u0590" <= c <= u"\u05EA" for c in name):
                name = name[::-1]
            names.append(name)
            counts.append(count)

        show_plot(counts, names)

    except Exception as e:
        dialog(str(e), "error")


def show_plot(counts, names):
    # Bring some raw data.
    frequencies = counts

    # In my original code I create a series and run on that,
    # so for consistency I create a series from the list.

    freq_series = pd.Series(frequencies)
    x_labels = names

    # Plot the figure.
    plt.figure(figsize=(16, 8))
    ax = freq_series.plot(kind='bar')
    ax.set_title('Message Counter for Whatssapp by users')
    ax.set_xlabel('Amount ($)')
    ax.set_ylabel('Frequency')
    ax.set_xticklabels(x_labels)

    rects = ax.patches

    # For each bar: Place a label
    for rect in rects:
        # Get X and Y placement of label from rect.
        y_value = rect.get_height()
        x_value = rect.get_x() + rect.get_width() / 2

        # Number of points between bar and label. Change to your liking.
        space = 10
        # Vertical alignment for positive values
        va = 'bottom'

        # Use Y value as label and format number with one decimal place
        label = y_value

        # Create annotation
        plt.annotate(
            label,  # Use `label` as label
            (x_value, y_value),  # Place label at end of the bar
            xytext=(0, space),  # Vertically shift label by `space`
            textcoords="offset points",  # Interpret `xytext` as offset in points
            ha='center',  # Horizontally center label
            va=va,  # Vertically align label differently for
            rotation='vertical')
        # positive and negative values.
    plt.show()


# ~~~~~~~~~~~~~~~~~~~

# ~~~~~~ GUI ~~~~~~~~

root = Tk()
root.title('WhatsApp Statistics')
root.geometry("550x140")

mf = Frame(root)
mf.pack()

f1 = Frame(mf, width=600, height=250)
f1.pack(fill=X)
f2 = Frame(mf, width=600, height=250)
f2.pack()

# File Path labels
file_path = StringVar()
Label(f1, text="Select Your File:").grid(row=0, column=0, sticky='e')
path_entry = Entry(f1, width=50, textvariable=file_path)
path_entry.grid(row=0, column=1, padx=2, pady=2, sticky='we', columnspan=25)
Button(f1, text="Browse", command=open_file).grid(row=0, column=27, padx=8, pady=4)

# Number Days Back filter
number_of_days = StringVar()
Label(f1, text="Messages in last days:").grid(row=1, column=0, sticky='e')
number_of_days_entry = Entry(f1, width=50, textvariable=number_of_days)
number_of_days_entry.grid(row=1, column=1, padx=2, pady=2, sticky='we', columnspan=25)
Label(f1, text="Leave empty for all messages").grid(row=2, column=0, sticky='e')
Button(f1, text="Browse", command=open_file).grid(row=0, column=27, padx=8, pady=4)

radio_var = IntVar()
radio_var.set(1)
Radiobutton(f1, text="Android", variable=radio_var, value=1).grid(row=3, column=1, sticky=W)
Radiobutton(f1, text="IPhone", variable=radio_var, value=2).grid(row=3, column=2, sticky=W)

# Buttons
Button(f2, text="Process", width=32, command=parse_txt_file).grid(row=0)

root.mainloop()
# ~~~~~~~~~~~~~~~~~~~
