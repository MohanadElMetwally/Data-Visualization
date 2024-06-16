import sys
import os
import gc
import customtkinter as ctk
import matplotlib.pyplot as plt
from data_visualization.plot_types import Plots
from data_visualization.data_loader import File, KaggleFile
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import (
    filedialog,
    messagebox,
    StringVar
)

class DataVisualizationWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.data = None
        self.canvas = None
        self.figure = None
        self.plotter = None
        self._center_screen()
        self.title("Data Visualization")
        self.resizable(False, False)

        self.create_import_section()

        self.create_data_columns_frame()

        self.create_plot_frame()
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        self.mainloop()

    def _on_closing(self) -> None:
        """Executes closes all canvas and closes the window when the exit icon is clicked."""
        plt.close('all')
        self.figure = None
        self.plotter = None
        self.canvas = None
        self.data = None
        self.destroy()
        sys.exit(0)

    def run(self, *args, **kwargs) -> None:
        """Run the application."""
        self.mainloop(*args, **kwargs)

    def _center_screen(self) -> None:
        width = 1100 # Width 
        height = 800 # Height
        
        screen_width = self.winfo_screenwidth()  # Width of the screen
        screen_height = self.winfo_screenheight() # Height of the screen
        
        # Calculate Starting X and Y coordinates for Window
        x = (screen_width/2) - (width/2) - 50
        y = (screen_height/2) - (height/2) - 50
        
        self.geometry('%dx%d+%d+%d' % (width, height, x, y))

    def create_import_section(self) -> None:
        """
        Creates a GUI section for dataset import options, including:

        - Radio buttons for local and Kaggle imports.
        - A text entry for file paths.
        - Browse and Download buttons for local and Kaggle datasets, respectively.
        """
        # Create the import frame
        self.import_frame = ctk.CTkFrame(master= self, width=250)
        self.import_frame.grid(row= 0, column=0, padx= 10, pady= 10, sticky= ctk.NSEW)

        # Add a label for the section
        self.import_label = ctk.CTkLabel(self.import_frame, text= 'Load dataset options:')
        self.import_label.grid(row= 0, column=0, padx= 10, pady= 5, sticky= ctk.W)

        # Create radio buttons for local and Kaggle imports
        self.import_option = ctk.StringVar(value= 'Local')
        self.radio_local = ctk.CTkRadioButton(self.import_frame, variable=self.import_option,
                                            value='Local', text= 'Load a Local Dataset',
                                            command=self.toggle_import_options)
        self.radio_local.grid(row= 1, column=0, padx= 10, pady= 10, sticky= ctk.W)
        self.radio_kaggle = ctk.CTkRadioButton(self.import_frame, variable=self.import_option,
                                            value='Kaggle', text='Download a Kaggle Dataset', 
                                            command=self.toggle_import_options)
        self.radio_kaggle.grid(row= 2, column=0, padx= 10, pady= 10, sticky= ctk.W)

        self.browse_frame = ctk.CTkFrame(self)
        self.browse_frame.grid(row= 0, column= 1, padx= 10, pady= 10, sticky= ctk.NSEW)
        
        self.download_progress_label = ctk.CTkLabel(self.browse_frame, text=' ')
        self.download_progress_label.place(x= 300, y= 10)
        self.plot_progress_label = ctk.CTkLabel(self.browse_frame, text=' ')
        self.plot_progress_label.place(x= 300, y= 10)

        self.entry_textvariable = ctk.StringVar()
        self.read_entry = ctk.CTkEntry(self.browse_frame, width=600,
                                        textvariable= self.entry_textvariable, state= 'readonly')
        self.read_entry.grid(row= 0, column=0, padx= 10, pady= 50)

        # Create a browse button for importing local dataset
        self.download_kaggle_btn = ctk.CTkButton(self.browse_frame, text='Download', command= self.download_dataset)
        self.download_kaggle_btn.grid(row= 0, column=1, padx= 10, pady= 50)
        self.download_kaggle_btn.grid_remove()
        self.local_read_btn = ctk.CTkButton(self.browse_frame, text= 'Browse', command= self.load_local_file)
        self.local_read_btn.grid(row= 0, column=1, padx= 10, pady= 50)


    def create_data_columns_frame(self) -> None:
        """
        Creates a scrollable frame to display information about numerical and categorical columns.
        """
        # Create the scrollable frame for numerical data type
        self.num_col_frame = ctk.CTkScrollableFrame(self, height= 150, width=230)
        self.num_col_frame.grid(row= 1, column= 0, padx= 10, pady= 10, sticky= ctk.NW)

        # Add labels for the numerical columns and unique values
        self.num_label = ctk.CTkLabel(self.num_col_frame, text= 'Numerical Columns')
        self.num_label.grid(row= 0, column=0, padx= 10, pady= 5, sticky= ctk.N)
        self.num_unique_label = ctk.CTkLabel(self.num_col_frame, text= 'Unique Values')
        self.num_unique_label.grid(row= 0, column=1, padx= 10, pady= 5, sticky= ctk.N)
        
        # Create the scrollable frame for categorical data type
        self.cat_col_frame = ctk.CTkScrollableFrame(self, height= 150, width=230)
        self.cat_col_frame.grid(row= 2, column= 0, padx= 10, pady= 10, sticky= ctk.NW)

        # Add labels for the categorical columns and unique values
        self.cat_label = ctk.CTkLabel(self.cat_col_frame, text= 'Categorical Columns')
        self.cat_label.grid(row= 0, column=0, padx= 10, pady= 5, sticky= ctk.N)
        self.cat_unique_label = ctk.CTkLabel(self.cat_col_frame, text= 'Unique Values')
        self.cat_unique_label.grid(row= 0, column=1, padx= 10, pady= 5, sticky= ctk.N)

    def load_local_file(self) -> None:
        """
        Prompts the user to select a local file, reads its data, and updates the GUI.

        Supported file types: CSV, JSON, Parquet, Excel, Pickle.

        Raises:
            ValueError: If an unsupported file type is selected.
        """
        file_path = filedialog.askopenfilenames(
            title="Select a File",
            filetypes=[
                ("CSV Files", "*.csv"),
                ("JSON Files", "*.json"),
                ("Parquet Files", "*.parquet"),
                ("Excel Files", ["*.xlsx","*.xls"]),  
                ("Pickle Files", ["*.pickle","*.pkl","*.p"]),
                ("All Files", "*.*")
            ]
        )
        if file_path:
            try:
                self.data = File().read(file_path[0])
                self.entry_textvariable.set(file_path[0])
                self.update_data_columns()
                self.enable_plot(self.plot_frame)
                # self.disable_load_option(self.import_frame)
            except ValueError as e:
                messagebox.showerror(
                    title="Unsupported File Type",
                    message=f"The selected file type is not supported. Please choose a file with a supported extension (CSV, JSON, Parquet, Excel, or Pickle)."
            )

    def download_dataset(self) -> None:
        """
        Downloads a dataset from Kaggle and updates the GUI.

        Prompts for Kaggle credentials if not already stored.
        Handles downloading, error cases, and loading the dataset.

        Raises:
            Exception: If an error occurs during Kaggle dataset download.
            ValueError: If an unsupported file type is selected.
        """
        if not os.path.exists('./kaggle.json'):
            CredentialsWindow().mainloop()

        url = self.read_entry.get()
        if not url:
            messagebox.showerror('Invalid URL', 'Please make sure the provided URL is valid.')
            return

        folder_path = './Datasets/' + url.split('/')[-1]
        false_dir = f"./Datasets/"
        false_dirs = list()
        for dir in url.split('/'):
            false_dir += f'{dir}/'
            false_dirs.append(false_dir)
        if not os.path.exists(folder_path):
            try:
                self.download_progress_label.configure(text='Downloading dataset. . .')
                self.update()
                # download_thread = threading.Thread(target=KaggleFile.download_kaggle_dataset, args=(url,))
                # download_thread.start()
                # download_thread.join()
                KaggleFile.download_kaggle_dataset(url= url)
                self.download_progress_label.configure(text=' ')
            except Exception as e:
                messagebox.showerror('Invalid URL!', 'Please make sure the provided URL is valid.')
                if false_dirs:
                    for dir in false_dirs[::-1]:
                        os.rmdir(dir)  # Delete the falsely created empty directory
                self.download_progress_label.configure(text=' ')
                return

            downloaded_datasets_list = os.listdir(folder_path)
            try:
                self.load_kaggle_dataset(folder_path, downloaded_datasets_list)
            except ValueError as e:
                messagebox.showerror(
                        title="Unsupported File Type",
                        message=f"The selected file type is not supported. Please choose a file with a supported extension (CSV, JSON, Parquet, Excel, or Pickle)."
                )
        else:
            downloaded_datasets_list = os.listdir(folder_path)
            messagebox.showinfo('Dataset found!', 'Dataset already exists!')
            self.load_kaggle_dataset(folder_path, downloaded_datasets_list)

    def load_kaggle_dataset(self, folder_path: str = None, downloaded_datasets_list: list[str] = None) -> None:
        """
        Loads a Kaggle dataset from a specified folder.

        If only one file is present, loads it directly.
        Otherwise, prompts the user to select a file.

        Args:
            folder_path (str): The path to the folder containing the dataset files.
            downloaded_datasets_list (list): A list of file names in the folder.

        Raises:
            ValueError: If an unsupported file type is selected.
        """
        if len(downloaded_datasets_list) == 1:
            file_path = f'{folder_path}/{downloaded_datasets_list[0]}'
            self.data = File().read(file_path)
            self._update_window()
        else:
            file_path = filedialog.askopenfilenames(
            title="Select a File",
            filetypes=[
                ("CSV Files", "*.csv"),
                ("JSON Files", "*.json"),
                ("Parquet Files", "*.parquet"),
                ("Excel Files", ["*.xlsx","*.xls"]),  
                ("Pickle Files", ["*.pickle","*.pkl","*.p"]),
                ("All Files", "*.*")
            ],
            initialdir= folder_path,
        )
            if file_path:
                try:
                    self.data = File().read(file_path[0])
                    self._update_window()
                except ValueError as e:
                    messagebox.showerror(
                        title="Unsupported File Type",
                        message=f"The selected file type is not supported. Please choose a file with a supported extension (CSV, JSON, Parquet, Excel, or Pickle)."
                )

    # changes some functionalities in the window after loading a kaggle dataset
    def _update_window(self) -> None:
        """
        Updates the GUI after loading a dataset.

        Refreshes data columns, enables plotting, disables loading options,
        and sets read-only states for certain widgets.
        """
        self.update_data_columns()
        self.enable_plot(self.plot_frame)
        # self.disable_load_option(self.import_frame)
        # self.read_entry.configure(state = 'readonly')
        # self.download_kaggle_btn.configure(state= 'disabled')

    def toggle_import_options(self) -> None:
        """
        Toggles the visibility of import options and read_entry state.

        Shows or hides local and Kaggle download buttons based on user selection,
        and also adjusts the read_entry widget to be either read-only or editable.
        """
        selected_option = self.import_option.get()
        if selected_option == 'Local':
            self.local_read_btn.grid()
            self.download_kaggle_btn.grid_remove()  
            self.read_entry.configure(state='readonly')
        else:
            self.local_read_btn.grid_remove()
            self.download_kaggle_btn.grid()  
            self.read_entry.configure(state='normal')

    def update_data_columns(self) -> None:
        """Updates numerical and categorical data columns."""

        def _update_frame(frame, cols, nunique_values):
            """Updates a frame with column information."""
            header_labels = frame.grid_slaves(row=0)  # Preserve header labels
            for child in frame.winfo_children():
                if child not in header_labels:
                    child.destroy()  # Clear only labels below header

            for i, col in enumerate(cols):
                label1 = ctk.CTkLabel(frame, text=col)
                label1.grid(row=i + 1, column=0, padx=10, sticky=ctk.N)
                label2 = ctk.CTkLabel(frame, text=nunique_values.iloc[i])
                label2.grid(row=i + 1, column=1, padx=10, sticky=ctk.N)

        # Update numerical columns
        num_cols = self.data.select_dtypes(include=['number']).columns
        num_nunique_values = self.data[num_cols].nunique()
        _update_frame(self.num_col_frame, num_cols, num_nunique_values)

        # Update categorical columns
        cat_cols = self.data.select_dtypes(include=['object']).columns
        cat_nunique_values = self.data[cat_cols].nunique()
        _update_frame(self.cat_col_frame, cat_cols, cat_nunique_values)

    def create_plot_frame(self) -> None:
        """
        Creates a GUI frame for plotting, including:

        - Entries for X, Y, and Hue values.
        - A dropdown menu for plot type selection.
        - A button to trigger the plotting process.
        """
        self.plot_frame = ctk.CTkFrame(self)
        self.plot_frame.grid(row= 1, column=1, padx= 10, pady= 10, sticky= ctk.NW)

        self.x_entry_label = ctk.CTkLabel(self.plot_frame, text= 'X value')
        self.x_entry_label.grid(row=0, column=0, padx=5, pady=5)
        self.x_entry = ctk.CTkEntry(self.plot_frame)
        self.x_entry.grid(row= 0, column=1, padx=11, pady = 5)

        self.y_entry_label = ctk.CTkLabel(self.plot_frame, text= 'Y value')
        self.y_entry_label.grid(row=0, column=2, padx=11, pady=5)
        self.y_entry = ctk.CTkEntry(self.plot_frame)
        self.y_entry.grid(row= 0, column=3, padx=5, pady = 5)

        self.hue_entry_label = ctk.CTkLabel(self.plot_frame, text= 'Hue')
        self.hue_entry_label.grid(row=1, column=0, padx=5, pady=5)
        self.hue_entry = ctk.CTkEntry(self.plot_frame)
        self.hue_entry.grid(row= 1, column=1, padx=11, pady = 5)

        self.plot_type_label = ctk.CTkLabel(self.plot_frame, text='Plot type')
        self.plot_type_label.grid(row=1, column=2)
        self.optionmenu_var = StringVar(value="Scatter")
        self.plot_type_optionmenu = ctk.CTkOptionMenu(self.plot_frame, 
                                                    values= ['Scatter', 'Histogram',
                                                            'Box','Count','Bar',],
                                                    variable= self.optionmenu_var)
        self.plot_type_optionmenu.grid(row=1, column= 3)
        self.optionmenu_var.trace_add("write", self._y_value_state)
        self.optionmenu_var.trace_add("write", self._y_value_clear)

        self.plot_btn = ctk.CTkButton(self.plot_frame, text= 'Plot graph', 
                                    command= self.plot_graph)
        self.plot_btn.grid(row=1, column= 4, padx= 12, pady= 5)

        for child in self.plot_frame.winfo_children():
            child.configure(state='disabled')


    def plot_graph(self) -> None:
        """Creates and displays a plot based on user-specified options."""
        # Get user-selected plot type
        plot_type = self.optionmenu_var.get()
        self.plotter = Plots(plot_type)

        # Retrieve plot data from user entries
        x_value = self.x_entry.get()
        y_value = self.y_entry.get() if plot_type in ['Scatter', 'Box', 'Bar'] else None
        hue = self.hue_entry.get() if self.hue_entry.get() else None

        plt.close('all')
        if self.canvas is not None:
            self.canvas.get_tk_widget().destroy()
            self.figure.clf()
            self.canvas = None
            self.figure = None
        gc.collect()

        try:
            self.plot_progress_label.configure(text= 'Plotting. . .')
            self.update()
            self.figure = plt.figure(figsize=(8, 5.5))
            self.plotter.plot(data=self.data, x=x_value, y=y_value, hue=hue)
            self.canvas = FigureCanvasTkAgg(self.figure, master=self)
            self.canvas.get_tk_widget().place(x= 315, y= 280)
            self.plot_progress_label.configure(text= ' ')
        except ValueError as e:
            messagebox.showerror(
            title= "Data Value Mismatch",
            message= "Oops! I couldn't find the specified X, Y, or Hue value in the dataset.\n"
            "Please double-check the values you entered, as they are case-sensitive.\n"
            "Here are some tips:\n"
            "- Review the column names in your dataset to ensure accuracy.\n"
            "- Ensure there are no typos or extra spaces in the values you entered.\n"
            '- Remember that case matters! "Column Name" is different from "column name".'
            )


    def enable_plot(self, child_list) -> None:
        """Enables plot widgets."""
        for child in child_list.winfo_children():
            child.configure(state= 'normal')
    
    def disable_load_option(self, child_list) -> None:
        """Disables plot widgets."""
        for child in child_list.winfo_children():
            child.configure(state= 'disabled')

    def _y_value_state(self, *args) -> None:
        """Disables y_entry if Count or Histogram plots is selected."""
        self.y_entry.configure(state= 'disabled') if self.optionmenu_var.get() in ['Count', 'Histogram'] else self.y_entry.configure(state= 'normal')

    def _y_value_clear(self, *args) -> None:
        """deletes any text in y_entry if Count or Histogram plots is selected."""
        self.y_entry.delete(0, 'end') if self.optionmenu_var.get() in ['Count', 'Histogram'] else None




class CredentialsWindow(ctk.CTk):
    """
    A class that creates a GUI window to collect and save Kaggle credentials.
    """
    def __init__(self) -> None:
        super().__init__()
        self.username = None
        self.key = None
        self.ask_credentials()
        self.mainloop()

    def ask_credentials(self) -> None:
        """
        Configures the window's layout, including labels, entry fields, and a button.
        Displays instructions for the user to enter their Kaggle credentials.
        """
        screen_width = self.winfo_screenwidth()  
        screen_height = self.winfo_screenheight()

        x = (screen_width/2) - (300/2) - 50
        y = (screen_height/2) - (200/2) - 50

        self.geometry('%dx%d+%d+%d' % (300, 200, x, y))
        self.title("Enter Kaggle Credentials")
        self.resizable(False, False)

        # Label with clear instructions
        self.instruction_label = ctk.CTkLabel(master=self, text="Enter your Kaggle credentials:")
        self.instruction_label.place(x = 10, y=10)

        # Entry widgets with placeholders
        self.username_label = ctk.CTkLabel(master=self, text="Username")
        self.username_label.place(x= 10, y= 50)
        self.username_entry = ctk.CTkEntry(master=self, width=200)
        self.username_entry.place(x = 80, y= 50)

        self.key_label = ctk.CTkLabel(master=self, text="Kaggle Key")
        self.key_label.place(x = 10, y= 90)
        self.key_entry = ctk.CTkEntry(master=self, width= 200, show= '*')
        self.key_entry.place(x = 80, y= 90)

        # # Save button with secure handling
        self.save_button = ctk.CTkButton(master=self, 
                                    text="Save", 
                                    command= self.save_information)
        self.save_button.place(x = 80 , y= 150)
        self.mainloop()

    def save_information(self):
        """
        Retrieve the entered username and key from the entry fields.
        Attempts to save the credentials as JSON file.
        Handles potential errors and displays success or error messages.
        """
        self.username = self.username_entry.get()
        self.key = self.key_entry.get()

        if self.username and self.key:
            try:
                KaggleFile.set_credentials(self.username, self.key)
                messagebox.showinfo("Success!", "Credentials saved successfully.")
                self.destroy()  # Close window if successful
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
        else:
            messagebox.showerror("Value Error", "Username or Key is incorrect!")
