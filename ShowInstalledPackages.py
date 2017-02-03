# Copyright <2016> <Larz60+>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in the
# Software without restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
import tkinter as tk
import tkinter.ttk as ttk
import pip
import requests
import json
import socket
import getpass


class ShowInstalledPackages:
    def __init__(self, root):
        self.s = ttk.Style()
        self.s.theme_use('classic')
        self.parent = root
        self.userid = getpass.getuser()
        self.package_name = None
        self.pkgs = None
        self.pkg_details = {}
        self.pkglist = None
        self.pkeys = []
        self.pkglist_filename = 'pkglist.json'
        self.PackageData_filename = 'PackageData.json'

        root.title('Installed packages for {}'.format(self.userid))
        self.internet_available = socket.gethostbyname(socket.gethostname()) != '127.0.0.1'

        # GUI prototypes
        self.fmain = tk.Frame
        self.bottom_frame = tk.Frame
        self.blabel = tk.Label
        self.blabeltxt = tk.StringVar()
        self.t1 = ttk.Treeview
        self.textframe = tk.Text
        self.txscroll = tk.Scrollbar

        # Geometry variables
        self.treeheight = 25
        self.mfheight = self.treeheight + 5
        self.bfheight = 5

        self.mfrow = 0
        self.mfcol = 0

        self.trrow = 0
        self.trcol = 0

        self.txrow = 0
        self.txcol = 0

        self.build_gui()

    def build_gui(self):
        self.create_main_frame()
        self.create_bottom_frame()
        self.create_treeframe()
        self.create_textframe()
        self.load_treeframe()

    def create_main_frame(self):
        self.fmain = tk.Frame(self.parent, bd=2, relief=tk.RAISED)
        self.fmain.grid(row=self.mfrow, rowspan=self.mfheight, column=self.mfcol,
                        padx=2, pady=2, sticky='nsew')
        self.mfrow += self.mfheight

    def create_bottom_frame(self):
        self.bottom_frame = tk.Frame(self.parent, bd=2, relief=tk.RAISED)
        self.bottom_frame.grid(row=self.mfrow, rowspan=self.bfheight, column=self.mfcol,
                               padx=2, pady=2, sticky='nsew')
        self.mfrow += self.bfheight
        self.blabel = tk.Label(self.bottom_frame, textvariable=self.blabeltxt, bd=2, relief=tk.SUNKEN)
        self.blabel.grid(row=0, rowspan=self.bfheight, column=0, sticky='nsew')

    def create_treeframe(self):
        treestyle = ttk.Style()
        treestyle.configure("Treeview.Heading", foreground='white',
                            background='SteelBlue', height=3)
        self.t1 = ttk.Treeview(self.fmain, height=self.treeheight,
                               padding=(2, 2, 2, 2),
                               columns='Version', style='Treeview',
                               selectmode="extended")
        self.t1.heading('#0', text='Package', anchor=tk.CENTER)
        self.t1.heading('#1', text='Version', anchor=tk.CENTER)
        self.t1.column('#0', stretch=tk.YES, minwidth=20, width=150)
        self.t1.column('#1', stretch=tk.YES, minwidth=10, width=70)

        self.t1.grid(row=0, rowspan=self.treeheight, column=0)
        treescrolly = tk.Scrollbar(self.fmain, orient=tk.VERTICAL,
                                   command=self.t1.yview)
        treescrolly.grid(row=0, rowspan=self.treeheight, column=1, sticky='ns')
        treescrollx = tk.Scrollbar(self.fmain, orient=tk.HORIZONTAL,
                                   command=self.t1.xview)
        treescrollx.grid(row=self.treeheight + 1, column=0, columnspan=2, sticky='ew')
        self.t1.configure(yscroll=treescrolly)
        self.t1.configure(xscroll=treescrollx)
        self.t1.bind('<Double-1>', self.pkg_selected)
        self.t1.bind('<ButtonRelease-1>', self.treeview_summary)

    def create_textframe(self):
        self.textframe = tk.Text(self.fmain, bd=2, bg='#CEF6EC',
                                 relief=tk.RAISED)
        self.txscroll = tk.Scrollbar(self.fmain, orient=tk.VERTICAL,
                                     command=self.textframe.yview)
        self.txscroll.grid(row=1, rowspan=self.treeheight, column=4, sticky='ns')
        self.textframe.configure(yscroll=self.txscroll.set)
        self.textframe.grid(row=0, rowspan=self.treeheight, column=3, padx=2,
                            pady=2, sticky='nsew')

    def load_treeframe(self):
        self.get_pkgs_from_pip()
        self.get_pks_details()
        for key in self.pkeys:
            if key in self.pkg_details:
                self.t1.insert('', 'end', text=key, values=self.pkglist[key])

    def treeview_summary(self, event):
        curitem = self.t1.focus()
        x = self.t1.item(curitem)
        self.package_name = x['text']
        sumdata = self.pkg_details[self.package_name]['summary']
        self.blabeltxt.set(sumdata)

    @staticmethod
    def get_package_info(pkgname):
        pypi_info_url = 'https://pypi.python.org/pypi/{}/json'.format(pkgname)
        response = requests.get(pypi_info_url)
        response.raise_for_status()
        jdata = json.loads(response.content.decode('utf-8'))
        return jdata
    
    def get_pkgs_from_pip(self):
        if not self.internet_available:
            with open(self.pkglist_filename, 'r') as f:
                self.pkglist = json.load(f)
        else:
            self.pkgs = pip.get_installed_distributions(local_only=True, include_editables=True,
                                                        editables_only=False, user_only=False)
            self.pkglist = dict()
            for item in self.pkgs:
                z = str(item).split()
                self.pkglist[z[0]] = z[1]

        if self.internet_available:
            with open(self.pkglist_filename, 'w') as f:
                json.dump(self.pkglist, f)

    def get_pks_details(self):
        if not self.internet_available:
            with open(self.PackageData_filename, 'r') as f:
                self.pkg_details = json.load(f)
            self.pkeys = list(self.pkglist.keys())
            self.pkeys.sort()
        else:
            self.pkeys = list(self.pkglist.keys())
            self.pkeys.sort()
            for key in self.pkeys:
                data = self.get_package_info(key)
                if data is None:
                    print("Rogue package {} has no body - Won't be listed".format(key))
                    continue
                self.pkg_details[key] = data['info']

        if self.internet_available:
            with open(self.PackageData_filename, 'w') as f:
                json.dump(self.pkg_details, f)

    def pkg_selected(self, event):
        curitem = self.t1.focus()
        x = self.t1.item(curitem)
        self.package_name = x['text']
        pn = self.pkglist[self.package_name]
        data = self.pkg_details[self.package_name]
        dkeys = list(data.keys())
        dkeys.sort()
        self.textframe.delete('1.0', tk.END)
        self.textframe.tag_configure('tag-center', justify='center')
        # Insert Title as first line
        self.textframe.insert('end', 'Package Name: {} -- Installed Version: {}\n'
                                     'Latest Version: {}\n'
                              .format(self.package_name, pn, data['version']), 'tag-center')
        self.display_data(data, dkeys)

    def display_data(self, data, dkeys):
        for key in dkeys:
            if key == 'version' or key == 'description':
                continue
            if isinstance(data[key], list):
                for element in data[key]:
                    displ = '    {} -- {}\n'.format(key, element)
                    self.textframe.insert(tk.END, displ)
                self.textframe.insert(tk.END, '\n')
                # print(f'Type List: {key} -- {data[key]}\n\n')
            elif isinstance(data[key], dict):
                for element in data[key].items():
                    displ = '    {} -- {}\n'.format(key, element)
                    self.textframe.insert(tk.END, displ)
                self.textframe.insert(tk.END, '\n')
                # print(f'Type Dict: {key} -- {data[key]}\n\n')
            else:
                displ = '{} -- {}\n\n'.format(key, data[key])
                self.textframe.insert(tk.END, displ)
        displ = '\n=========================================================\n' \
                'Description -- {}\n\n'.format(data['description'])
        self.textframe.insert(tk.END, displ)

    @staticmethod
    def show_widget_values(target_widget):
        wkeys = list(target_widget.keys())
        wkeys.sort()
        for key in wkeys:
            print('key: {} value: {}'.format(key, target_widget[key]))


def main():
    root = tk.Tk()
    ShowInstalledPackages(root)
    root.mainloop()

if __name__ == '__main__':
    main()
