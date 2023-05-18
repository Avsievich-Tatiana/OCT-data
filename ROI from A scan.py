import numpy as np
import matplotlib.pyplot as plt
import re
from tkinter import Tk, filedialog, Button, Label, Frame, StringVar
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


class Application(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)  # Handle window closing
        self.pack()
        self.create_widgets()

        # Define file_path as an instance variable
        self.file_path = StringVar()
        self.roi_points = []  # Initialize the roi_points list
        self.a_scan_bounds = (0, 0, 0, 0)  # (xmin, xmax, ymin, ymax)
        self.roi_lines = []  # Initialize the roi_lines list
        self.roi_texts = []  # Initialize the roi_texts list

    def load_file(self):
        # Use the set method to change the value of file_path
        self.file_path.set(filedialog.askopenfilename())
        self.display_plots()

    def display_plots(self):
        # Extract dimensions from the file name
        match = re.search(r'X(\d+) Y(\d+) Z(\d+)', self.file_path.get())
        if match:
            X = int(match.group(1))
            frames = int(match.group(2))
            Z = int(match.group(3))
        else:
            raise ValueError("Could not extract dimensions from the file name")

        # Open file and read data 1D array
        with open(self.file_path.get(), 'rb') as f:
            a = np.fromfile(f, dtype='float64')

        # Reshape data into 3D array
        b = a.reshape((Z, X, frames), order='F')

        # Calculate average image
        img_avg = np.mean(b, axis=2)

        # Calculate A-scan
        a_scan = np.sum(img_avg, axis=1)
        # Calculate A-scan
        self.a_scan = np.sum(img_avg, axis=1)

        # Clear previous plots
        self.axs[0].clear()
        self.axs[1].clear()

        # Plot averaged image on the first subplot
        self.axs[0].imshow(img_avg, cmap='gray')
        self.axs[0].set_title('Averaged image')
        self.axs[0].set_xlabel('X')
        self.axs[0].set_ylabel('Depth (Z)')

        # Plot A-scan on the second subplot
        self.axs[1].plot(range(Z), a_scan)
        self.axs[1].grid(True)  # Add grid to the A-scan plot
        self.axs[1].set_title('Summed A-scan')
        self.axs[1].set_xlabel('Depth (Z)')
        self.axs[1].set_ylabel('Intensity')

        # Get the bounds of the A-scan plot
        self.a_scan_bounds = self.axs[1].get_xlim() + self.axs[1].get_ylim()  # (xmin, xmax, ymin, ymax)


        # Draw the figures on the canvas
        self.canvas.draw()

    def add_roi(self):
        print("Please click on two points on the plot to define the ROI")

        def onclick(event):
            if event.inaxes == self.axs[1]:
                self.roi_points.append(int(event.xdata))

                if len(self.roi_points) == 2:
                    roi_start, roi_end = sorted(self.roi_points)
                    self.roi_points = []

                    roi_range = np.arange(roi_start, roi_end + 1)
                    fit = np.polyfit(roi_range, self.a_scan[roi_start:roi_end+1], 1)

                    slope = fit[0]
                    intercept = fit[1]

                    line_points = slope * roi_range + intercept

                    equation_text = f"y = {slope:.2f}x + {intercept:.2f}"
                    
                    text = self.axs[1].text(roi_start, self.a_scan[roi_start], f'Slope: {slope:.2f}\n{equation_text}', 
                                color='red', va='top')
                    self.roi_texts.append(text)

                    line, = self.axs[1].plot(roi_range, line_points, 'r--', linewidth=2)
                    self.roi_lines.append(line)

                    self.fig.canvas.draw()

        self.cid = self.fig.canvas.mpl_connect('button_press_event', onclick)

    def remove_roi(self):
        if self.roi_lines:
            line = self.roi_lines.pop()  # Remove the last line from the list
            line.remove()  # Remove the line from the plot

            if self.roi_texts:  # Check if there are any texts
                text = self.roi_texts.pop()  # Remove the last text from the list
                text.remove()  # Remove the text from the plot

            self.fig.canvas.draw()  # Update the plot

            # Disconnect the 'button_press_event'
            self.fig.canvas.mpl_disconnect(self.cid)

    def create_widgets(self):
    # Creating a frame for the buttons
        root.resizable(True, True)

        self.button_frame = Frame(self)
        self.button_frame.grid(row=0, column=0, sticky='n')  # Place the frame at the top of column 0

        # Creating the "Open" button
        self.open_button = Button(self.button_frame, width=10)  # Set the width of the button
        self.open_button["text"] = "Open"
        self.open_button["command"] = self.load_file
        self.open_button.grid(row=0, column=0)  # Set the position of the button

        # Creating the "Choose ROI" button
        self.roi_button = Button(self.button_frame, width=10)  # Set the width of the button
        self.roi_button["text"] = "Choose ROI"
        # Connect this button to the function that will handle the "Choose ROI" action
        # self.roi_button["command"] = choose_roi
        self.roi_button.grid(row=1, column=0)  # Set the position of the button

        # Creating the "Remove ROI" button
        self.remove_roi_button = Button(self.button_frame, width=10)  # Set the width of the button
        self.remove_roi_button["text"] = "Remove ROI"
        self.remove_roi_button["command"] = self.remove_roi
        # Connect this button to the function that will handle the "Remove ROI" action
        # self.remove_roi_button["command"] = remove_roi
        self.remove_roi_button.grid(row=2, column=0)  # Set the position of the button


        # Creating the Frame for the image and the A-scan plot
        self.plot_frame = Frame(self)
        self.plot_frame.grid(row=0, column=1, rowspan=3)

        # Creating the Figure and axes for the image and the A-scan plot
        self.fig, self.axs = plt.subplots(2, 1, figsize=(8, 10))

        # Creating the canvas for the image and the A-scan plot
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plot_frame)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side="top", fill="both", expand=True)

        # Add the toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, self.plot_frame)
        toolbar.update()

        # Add the "Choose ROI" button
        self.roi_button["command"] = self.add_roi

        # Add a label to display the slope
        self.slope_label = Label(self, text="Slope: ")
        self.slope_label.grid(row=3, column=0)

    def on_closing(self):
        plt.close("all")  # Close all Matplotlib figures
        self.master.destroy()  # Destroy the tkinter window


root = Tk()
app = Application(master=root)
app.mainloop()
