import psycopg2
import tkinter
from tkinter import ttk

conn = psycopg2.connect(dbname="databasename", user="postgres", port="5432")
cur = conn.cursor()

class Scrollbox(tkinter.Listbox):

    def __init__(self, window, **kwargs):
        super().__init__(window, **kwargs)

        self.scrollbar = tkinter.Scrollbar(window, orient=tkinter.VERTICAL, command=self.yview)


    def grid(self, row, column, sticky='nsw', rowspan=1, columnspan=1, **kwargs):
        super().grid(row=row, column=column, sticky=sticky, rowspan=rowspan, columnspan=columnspan, **kwargs)
        self.scrollbar.grid(row=row, column=column, sticky='nse', rowspan=rowspan, columnspan=columnspan)
        self['yscrollcommand'] = self.scrollbar.set


def connect_to_db():
    try:
        conn = psycopg2.connect(dbname=db_name.get(), user=db_user.get(), port=db_port.get(), host=db_host.get(), password=db_pass.get())
        cur = conn.cursor()
        get_tables()
        message_label.configure(text='Successfully connected')
    except:
        message_label.configure(text='Failed to connect to db')


def get_tables():
    try:
        cur.execute('SELECT * FROM pg_catalog.pg_tables WHERE schemaname = \'public\' ORDER BY tablename ASC;')
        tables = cur.fetchall()

        tableList.insert(tkinter.END, "Getting tables...")
        
        tableList.delete(0, tkinter.END)

        for table in tables:
            tableList.insert(tkinter.END, table[1])

        tableList.bind('<<ListboxSelect>>', get_rows)
        message_label.configure(text='Retrieved tables')
    except:
        message_label.configure(text='You broke something somehow.')


def get_rows(event):
    try:
        lb = event.widget
        index = lb.curselection()[0]
        table_name = lb.get(index)
        rowLV.delete(*rowLV.get_children())
        query = "SELECT * FROM {} ORDER BY id DESC LIMIT 100;".format(table_name)
        run_a_query(query)
        message_label.configure(text='Retrieved rows')
    except:
        message_label.configure(text='You broke something, most likely that table does not have an id column')
        

def query_the_db():
    try:
        query = query_box.get("1.0",tkinter.END)
        run_a_query(query)
        message_label.configure(text='Query executed successfully')
    except:
        message_label.configure(text='You broke something')


def run_a_query(query):
    cur.execute(query)
    colnames = [desc[0] for desc in cur.description]
    rowLV.delete(*rowLV.get_children())
    rowLV["columns"] = colnames
    for column in colnames:
        rowLV.column(column, minwidth=30, stretch=0)
        rowLV.heading(column, text=column)

    rows = cur.fetchall()
    for row in rows:
        attributes = []
        for attribute in row:
            attributes.append(attribute)
        rowLV.insert("", 'end', text=row[0], values=attributes)


mainWindow = tkinter.Tk()
mainWindow.title('DB Browser')
mainWindow.geometry('1024x1024')

mainWindow.columnconfigure(0, weight=1)
mainWindow.columnconfigure(1, weight=5)
mainWindow.columnconfigure(2, weight=5)
mainWindow.columnconfigure(3, weight=1) 
mainWindow.columnconfigure(4, weight=1)

mainWindow.rowconfigure(0, weight=1)
mainWindow.rowconfigure(1, weight=5)
mainWindow.rowconfigure(2, weight=5)
mainWindow.rowconfigure(3, weight=1)

# ===== labels =====
lbl_name = tkinter.Label(mainWindow, text="DB: ")
lbl_name.grid(row=0, column=0, sticky='nw')
db_name = tkinter.Entry()
db_name.insert(0, 'mlearnp-dev-droppable')
db_name.grid(row=0, column=0, sticky='sw')

lbl_host = tkinter.Label(mainWindow, text="Host: ")
lbl_host.grid(row=0, column=1, sticky='nw')
db_host = tkinter.Entry()
db_host.insert(0, '127.0.0.1')
db_host.grid(row=0, column=1, sticky='ne')

lbl_port = tkinter.Label(mainWindow, text="Port: ")
lbl_port.grid(row=0, column=1, sticky='sw')
db_port = tkinter.Entry()
db_port.insert(0, '5434')
db_port.grid(row=0, column=1, sticky='se')

lbl_user = tkinter.Label(mainWindow, text="User: ")
lbl_user.grid(row=0, column=2, sticky='nw')
db_user = tkinter.Entry()
db_user.insert(0, 'postgres')
db_user.grid(row=0, column=2, sticky='ne')

lbl_pass = tkinter.Label(mainWindow, text="Password: ")
lbl_pass.grid(row=0, column=2, sticky='sw')
db_pass = tkinter.Entry()
db_user.insert(0, '')
db_pass.grid(row=0, column=2, sticky='se')

tkinter.Button(mainWindow, text='Connect', command=connect_to_db).grid(row=0, column=4, sticky='wn')

# ===== Tables Listbox =====
tableList = Scrollbox(mainWindow)
tableList.grid(row=1, column=0, padx=(0, 0))
tableList.config(border=2, relief='sunken')

# ===== Rows Listbox =====
rowLV = ttk.Treeview(mainWindow)
rowLV.grid(row=2, column=0, columnspan=5, padx=(0, 0))

# ===== Query box =====
query_box = tkinter.Text()
query_box.grid(row=1, column=1, columnspan=4, sticky='nsew', padx=(0, 0))
query_box.config(border=2, relief='sunken')
tkinter.Button(mainWindow, text='Query', command=query_the_db).grid(row=0, column=4, sticky='ws')

# ==== Message Box ====
message_label = tkinter.Label(mainWindow, text="message")
message_label.grid(row=2, column=1, columnspan=5, sticky='s')

# ===== Main loop =====
get_tables()

mainWindow.mainloop()
print("closing database connection")
cur.close()
conn.close()
