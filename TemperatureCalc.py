from tkinter import Tk
from tkinter.filedialog import *
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

class Adjustable: #Makes one Label + Textbox Line
    def __init__(self, master, name, initvalue):
        sv = StringVar()
        self.frame = Frame(master)
        self.frame.pack(fill=X, padx = 5)
        self.label = Label(self.frame, text=name)
        self.label.pack(side=LEFT)
        self.entry = Entry(self.frame, textvariable=sv, validate="focusout", validatecommand=self.callback)
        self.entry.pack(side=RIGHT)
        self.entry.delete(0, END)
        self.entry.insert(0, str(initvalue))

    def callback(self):
        Window1.calculate()
        return True

    def get(self):
        return float(self.entry.get())

class Window: #Handels all the Stuff in the adjustments window
    def __init__(self, master):
        adjustments = Frame(master)
        adjustments.pack(side=LEFT)

        spacer = Label(adjustments, text="Heat Gain ")
        spacer.pack()

        self.master=master
        self.Power1 = Adjustable(adjustments, "Type 1 Power  (W)", 12800)
        self.Efficiency1 = Adjustable(adjustments, "Type 1 Efficiency  (%)", 0.02)
        self.Power2 = Adjustable(adjustments, "Type 2 Power  (W)", 1600)
        self.Efficency2 = Adjustable(adjustments, "Type 2 Efficienzy  (%)", 0.4)
        self.UseMod = Adjustable(adjustments, "Usage Modifier  (%)", 0.27)

        spacer = Label(adjustments, text="")
        spacer.pack()

        self.AudiencePower = Adjustable(adjustments, "Audience Type  (W)", 80)
        self.AudienceCount = Adjustable(adjustments, "Audience Number", 220)

        spacer = Label(adjustments, text="Heat Loss")
        spacer.pack()

        self.BarrierTemperature = Adjustable(adjustments, "Barrier Outside Temperature  ("+u'\N{DEGREE SIGN}'+"C)", 23)
        self.Conductivity = Adjustable(adjustments, "Barrier K-Value  (W / mK)" ,0.6)
        self.Area = Adjustable(adjustments, "Barrier Area  (m"+u'\N{SUPERSCRIPT TWO}'+")" ,1105)
        self.WallThickness = Adjustable(adjustments, "Barrier Thickness  (m)" ,0.14)

        spacer = Label(adjustments, text="")
        spacer.pack()

        self.AirTemperature = Adjustable(adjustments, "Fresh Air Temperature ("+u'\N{DEGREE SIGN}'+"C)", 23)
        self.Vflow = Adjustable(adjustments, "Air Ventilation Volume  (m"+u'\N{SUPERSCRIPT THREE}'+" / h)" ,10000)
        self.P = Adjustable(adjustments, "Air Density  (Kg / m"+u'\N{SUPERSCRIPT THREE}'+")" ,1.275)
        self.C = Adjustable(adjustments, "Air Specific Heat Capacity  (KJ / KgK)" ,1.003)
        self.AirMass = Adjustable(adjustments, "Air Mass  (Kg)" ,3200)

        spacer = Label(adjustments, text="Simulation")
        spacer .pack()

        self.StartingTemperature = Adjustable(adjustments, "Starting Temperature ("+u'\N{DEGREE SIGN}'+"C)", 24.3)
        self.DeltaTime = Adjustable(adjustments, "Time Intervals  (s)", 60)
        self.Recursions = Adjustable(adjustments, "Recursions" ,100)

        spacer = Label(adjustments, text="")
        spacer.pack()

        calcb = Button(adjustments, text="Export Data", command=self.export)
        calcb.pack()

        self.output = Frame(self.master)
        self.output.pack(side=LEFT)

    def calculate(self):
        #Get Values out of all the textboxes
        P1 = self.Power1.get()
        E1 = self.Efficiency1.get()
        P2 = self.Power2.get()
        E2 = self.Efficency2.get()
        UseMod = self.UseMod.get()

        Count = self. AudiencePower.get()
        Type = self.AudienceCount.get()

        BarrierTemperature = self.BarrierTemperature.get()
        StartingTemperature = self.StartingTemperature.get()
        Conductivity = self.Conductivity.get()
        Area = self.Area.get()
        WallThickness = self.WallThickness.get()

        AirTemperature = self.AirTemperature.get()
        Vflow = self.Vflow.get()
        P = self.P.get()
        C = self.C.get()
        C2778 = 0.278
        Mass = self.AirMass.get()

        DTime = self.DeltaTime.get()
        Recursions = int(self.Recursions.get())
        t = 0


        #in the DAta list all recursions will be saved
        self.Datax = [0]
        self.Datay = [StartingTemperature]
        
        for x in range(0, Recursions):
            #Values that need to be calculated recursivly
            ddBarrierTemperature = StartingTemperature - BarrierTemperature
            ddAirTemperature = StartingTemperature - AirTemperature

            m1dPower = (P1*(1-E1) + P2*(1-E2)) * UseMod
            m2dPower = Count * Type
            m3dPower = -(Conductivity*Area*ddBarrierTemperature / WallThickness)
            m4dPower = -(ddAirTemperature*Vflow*P*C*C2778)

            #Total Energiy In/Out
            dEnergy = (m1dPower+m2dPower+m3dPower+m4dPower)*DTime

            #Temperature Change
            dTemperature = dEnergy / (1000*C*Mass)

            #Absolute Values
            StartingTemperature += dTemperature
            t += DTime 

            #Save Data
            self.Datax.append(t)
            self.Datay.append(StartingTemperature)

        for widget in self.output.winfo_children():
            widget.destroy()

        f = Figure(figsize=(5,5), dpi=100)
        a = f.add_subplot(111)
        a.plot(self.Datax, self.Datay)

        canvas = FigureCanvasTkAgg(f, self.output)
        canvas.draw()
        canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)

        toolbar = NavigationToolbar2Tk(canvas, self.output)
        toolbar.update()
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)

    def export(self):
        self.calculate()
        ExportString = ""
        for n in range(0,len(self.Datax)):
            ExportString += str(self.Datax[n]) + "," + str(self.Datay[n]) + "\n"
        OutputDir = askdirectory()
        if OutputDir != "":
            UniverseFile = open(str(OutputDir) +"/Export.csv", "w")
            UniverseFile.write(ExportString)
            UniverseFile.close()

root = Tk()
root.title("Temperature Flow")
Window1 = Window(root)
root.mainloop()
