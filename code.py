import tkinter as tk
from tkinter import ttk
import requests
from bs4 import BeautifulSoup
from pygooglenews import GoogleNews

# Initialize Google News
gn = GoogleNews(lang='en', country='IN')

# Create the main window
my_w = tk.Tk()
my_w.title('DEPARTMENT OF INFORMATION TECHNOLOGY')
my_w['bg'] = 'black'
my_w.attributes('-zoomed', True)

from time import strftime


def get_titles():
    search = gn.search("sports")
    newsitem = search['entries']
    c = 0
    mydata = "NEWS: \n"
    for item in newsitem[:15]:
        if c > 1:
            mydata = mydata + "\n" + item.title
        c = c + 1
    l3.config(text=mydata)
    l3.after(200000, get_titles)  # Call the function periodically


def my_time():
    time_string = strftime('%H:%M:%S %p \n %A \n %x')  # time format
    l1.config(text=time_string)
    l1.after(1000, my_time)

def fetch_table_data(url, max_rows=15):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve content from {url}")
        return []
    
    soup = BeautifulSoup(response.content, "html.parser")
    table = soup.find('table')
    
    if not table:
        print("No table found on the page.")
        return []
    
    rows = table.find_all('tr')
    
    table_data = []

    for row in rows:
        cols = row.find_all('td')
        cols = [(col.get_text(strip=True)).strip("Read More") for col in cols]
        
        if cols:
            if len(cols) > 1:
                first_column = cols.pop(0)  # Move the first column to last
                last_column = cols.pop(-1)  # Move the last column to last
                cols.append(first_column)
                cols.append(last_column)
            
            table_data.append(cols)
    
    return table_data[:max_rows]


# Function to fetch data and populate the Treeview widget
def get_sym():
    url = "https://www.knowafest.com/explore/upcomingfests"  # Replace with the actual URL

    table_data = fetch_table_data(url)

    if table_data:
        # Clear all existing rows in the Treeview
        for row in tree.get_children():
            tree.delete(row)

        # Insert new rows into the Treeview (ignoring the second column)
        for row in table_data:
            if len(row) > 1:
                # Insert only the first, third, and fourth columns
                tree.insert('', 'end', values=(row[0], row[2], row[3],row[4]))
    else:
        print("No data to display.")
    
    tree.after(100000, get_sym)  # Call the function periodically


# Create labels and widgets
my_font = ('times', 40, 'bold')  # Display size and style
my_font1 = ('times', 10, 'bold')
my_font2 = ('times', 8)

l1 = tk.Label(my_w, font=my_font, bg='black', fg='white')
l1.place(x=450, y=200)

l2 = tk.Label(my_w, text="              DEPARTMENT OF", font=('times', 30, 'bold'), bg='black', fg='white')
l2.place(x=50, y=10)
l21 = tk.Label(my_w, text="INFORMATION TECHNOLOGY", font=('times', 30, 'bold'), bg='black', fg='white')
l21.place(x=50, y=50)
l3 = tk.Label(my_w, font=my_font1, bg='black', fg='white')
l3.place(x=10, y=750, width=700)


style = ttk.Style()
style.configure("Treeview", font=('times', 10), background="black", foreground="white", fieldbackground="black")
style.configure("Treeview.Heading", font=('times', 10, 'bold'), background="black", foreground="white")  # Header
style.map("Treeview", background=[('selected', 'gray')])  # Selected row background color

tree = ttk.Treeview(my_w, columns=("Column 1", "Column 3", "Column 4","Column 5"), show="headings", height=15)
tree.place(x=10, y=400, width=700, height=250)


tree.heading("Column 1", text="Conference")
tree.heading("Column 3", text="Location")
tree.heading("Column 4", text="START")
tree.heading("Column 5", text="END")

tree.column("Column 1", width=200, anchor='w')  
tree.column("Column 3", width=318, anchor='w')  
tree.column("Column 4", width=16, anchor='w')  
tree.column("Column 5", width=16, anchor='w')  


my_time()
get_titles()
get_sym()

# Start the Tkinter main loop
my_w.mainloop()
