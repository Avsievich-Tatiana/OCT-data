#Import modules with corresponding classes and fucntions
import numpy as np
import matplotlib.pyplot as plt
import re
from tkinter import ttk, Tk, filedialog, Button, Label, Frame, StringVar
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.widgets import Cursor

class Application(Frame):
    def __init__(self, master=None): # main app window
        super().__init__(master)
        self.master = master # organize all widgets in a hierarchy
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)  # when user is closing window 
        self.pack()
        self.create_widgets() # create parts of the GUI
        self.file_path = StringVar() # Define file_path as an instance variable
        self.roi_points = []  # Initialize the roi_points list
        self.a_scan_bounds = (0, 0, 0, 0)  # (xmin, xmax, ymin, ymax) bounds for A-scan plot
        self.roi_lines = []  # Initialize the roi_lines list
        self.roi_texts = []  # Initialize the roi_texts list
        self.measurements = []  # Initialize the measurements list
        self.Z = 0
        self.a_scan = None # Initialize self.a_scan

    def load_file(self): # choose file and update self.file_path to store the chosen file's path
        self.file_path.set(filedialog.askopenfilename())
        self.display_plots()

    def display_plots(self):
        # Extract dimensions from the file name
        match = re.search(r'X(\d+) Y(\d+) Z(\d+)', self.file_path.get())
        if match:
            X = int(match.group(1))
            frames = int(match.group(2))
            self.Z = int(match.group(3))
        else:
            raise ValueError("Could not extract dimensions from the file name")

        # Open .dat file and read data 1D array
        with open(self.file_path.get(), 'rb') as f:
            a = np.fromfile(f, dtype='float64')

        # Reshape data into 3D array
        b = a.reshape((self.Z, X, frames), order='F')

        # Calculate average image: sum up all the frames (axis 2) of the image
        img_avg = np.mean(b, axis=2)
        # Calculate A-scan
        self.a_scan = np.sum(img_avg, axis=1)

        # Set up the plots
        self.axs[0].clear()
        self.axs[1].clear()

        x_um = np.linspace(0, 3000, X) # convert lines to mm scan width
        z_um = np.linspace(0, 1474, self.Z) # px to um (deoth)

        # Plot averaged image on the first subplot
        im = self.axs[0].imshow(img_avg, cmap='gray', extent=[x_um.min(), x_um.max(), z_um.max(), z_um.min()])
        self.axs[0].set_title('OCT image')
        self.axs[0].set_xlabel('Width (um)')
        self.axs[0].set_ylabel('Optical depth (um)')

        # Plot A-scan on the second subplot
        self.axs[1].plot(z_um, self.a_scan)
        self.axs[1].grid(True)  # Add grid to the A-scan plot
        self.axs[1].set_title('A-scan')
        self.axs[1].set_xlabel('Optical depth (um)')
        self.axs[1].set_ylabel('Intensity (a.u.)')

        # Get the bounds of the A-scan plot
        self.a_scan_bounds = self.axs[1].get_xlim() + self.axs[1].get_ylim()  # (xmin, xmax, ymin, ymax)

        # Draw the figures on the canvas
        self.canvas.draw()

    def add_roi(self):
            print("Please click on two points on the A-scan plot to define the ROI")
            self.cursor = Cursor(self.axs[1], useblit=True, color='red', linewidth=1)
            self.fig.canvas.draw()
            self.cursor.set_active(True) 

            def onclick(event):
                if event.inaxes == self.axs[1]: self.roi_points.append(int(event.xdata)) # x-coord of the click is added to the list

                if len(self.roi_points) == 2:
                    roi_start, roi_end = sorted(self.roi_points)
                    self.roi_points = []

                    roi_start_px = int(roi_start * self.Z / 1474)  
                    roi_end_px = int(roi_end * self.Z / 1474) 

                    roi_range = np.linspace(roi_start, roi_end, roi_end_px - roi_start_px + 1)
                    fit = np.polyfit(roi_range, self.a_scan[roi_start_px:roi_end_px+1], 1)

                    slope = fit[0]
                    intercept = fit[1]

                    line_points = slope * roi_range + intercept

                    equation_text = f"y = {slope:.2f}x + {intercept:.2f}"

                    text = self.axs[1].text(roi_start, self.a_scan[roi_start_px], f'Slope: {slope:.2f}\n{equation_text}', color='red', va='top')
                    self.roi_texts.append(text)

                    line, = self.axs[1].plot(roi_range, line_points, 'r--', linewidth=2)
                    self.roi_lines.append(line)

                    # Append the new measurement
                    self.measurements.append((len(self.measurements)+1, slope))
                    self.update_table()

                    self.fig.canvas.draw()

            self.cid = self.fig.canvas.mpl_connect('button_press_event', onclick)

    def remove_roi(self):
        if self.roi_lines:
            line = self.roi_lines.pop()  # Remove the last line from the list
            line.remove()  # Remove the line from the plot

            if self.roi_texts:  # Check if there are any texts
                text = self.roi_texts.pop()  # Remove the last text from the list
                text.remove()  # Remove the text from the plot

            # Deactivate the cursor
            self.cursor.set_active(False)
            self.fig.canvas.draw()

            # Disconnect the 'button_press_event'
            self.fig.canvas.mpl_disconnect(self.cid)

            if self.measurements:  # Check if there are any measurements
                self.measurements.pop()  # Remove the last measurement from the list
                self.update_table()  

    def update_table(self):
        # Clear the table
        for i in self.table.get_children():
            self.table.delete(i)

        # Add to the table
        for measurement in self.measurements:
            self.table.insert('', 'end', values=measurement)

        # Calculate the average slope and st dev
            if self.measurements:  # Check if the measurements list is not empty
                slopes = [item[1] for item in self.measurements]
                avg_slope = np.mean(slopes)
                std_dev = np.std(slopes)

        avg_slope_display = f"{avg_slope:.2f} ± {std_dev:.2f}"
        self.table.insert('', 'end', values=("Average", avg_slope_display))

    def create_widgets(self):
        self.master.resizable(True, True)

        self.button_frame = Frame(self)
        self.button_frame.grid(row=0, column=0, sticky='n', rowspan=4)  # Place the frame at the top of column 0

        # "Open" button
        self.open_button = Button(self.button_frame, width=10)
        self.open_button["text"] = "Open"
        self.open_button["command"] = self.load_file
        self.open_button.grid(row=0, column=0)

        # "Choose ROI" button
        self.roi_button = Button(self.button_frame, width=10)
        self.roi_button["text"] = "Choose ROI"
        self.roi_button["command"] = self.add_roi
        self.roi_button.grid(row=1, column=0)

        # "Remove ROI" button
        self.remove_roi_button = Button(self.button_frame, width=10)
        self.remove_roi_button["text"] = "Remove ROI"
        self.remove_roi_button["command"] = self.remove_roi
        self.remove_roi_button.grid(row=2, column=0) 

        # Creating the Frame for the image and the A-scan plot
        self.plot_frame = Frame(self)
        self.plot_frame.grid(row=0, column=1, rowspan=4)

        # Creating the Figure and axes for the image and the A-scan plot
        self.fig, self.axs = plt.subplots(2, 1, figsize=(8, 10))

        # Creating the canvas for the image and the A-scan plot
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)  # A tk.DrawingArea.
        self.canvas.draw()
        
        # Add the toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True) #Fixed

        # Create the cursor
        self.cursor = Cursor(self.axs[1], useblit=True, color='red', linewidth=1)
        self.cursor.set_active(False)  # Deactivate the cursor

        # Add a label to display the slope
        self.slope_label = Label(self.button_frame, text="Slope: ")
        self.slope_label.grid(row=3, column=0)

        # Creating a table for the measurements
        self.table = ttk.Treeview(self.button_frame, columns=('Measurement', 'Attenuation coef'), show='headings')
        self.table.column('Measurement', width=80, anchor='center')
        self.table.column('Attenuation coef', width=80, anchor='center')
        self.table.heading('Measurement', text='Measurement')
        self.table.heading('Attenuation coef', text='Attenuation coef')
        self.table.grid(row=4, column=0, sticky='nsew')  # Place the table below the buttons

    def on_closing(self):
        plt.close("all")  # Close all Matplotlib figures
        self.master.destroy()  # Destroy the tkinter window


root = Tk()
app = Application(master=root)
app.mainloop()