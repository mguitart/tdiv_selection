import matplotlib.pyplot as plt
import numpy as np
import matplotlib
from matplotlib import cm


class Colors:

    def __init__(self, color, label):
        self.names = None
        self.c = None
        self.min = None
        self.max = None
        self.norm = matplotlib.colors.LogNorm()
        self.cmap = plt.cm.RdYlGn
        self.cmap2 = color
        fig,ax = plt.subplots()
        self.fig = fig
        self.ax = ax
        self.sc = None
        self.eb = None

        self.T_div = []
        self.vel = []
        self.x_err = []
        self.y_err = []
        self.colors = []
        self.labels = []
        self.spec = None
        self.los = None
        self.label = label
        self.hovers = []

        self.annot = ax.annotate("", xy=(0,0), xytext=(20,20),textcoords="offset points",
                            bbox=dict(boxstyle="round", fc="w"),
                            arrowprops=dict(arrowstyle="->"))
        self.annot.set_visible(False)

    def update_annot(self, ind):
        pos = self.sc.get_offsets()[ind["ind"][0]]
        self.annot.xy = pos
        text = "{}".format(" ".join([self.names[n] for n in ind["ind"]]))
        self.annot.set_text(text)
        self.annot.get_bbox_patch().set_facecolor(self.cmap(self.norm(self.c[ind["ind"][0]])))
        self.annot.get_bbox_patch().set_alpha(0.4)

    def doHovers(self, event):
        for h in self.hovers:
            h.hover(event)

    def hover(self, event):
        vis = self.annot.get_visible()
        if event.inaxes == self.ax:
            cont, ind = self.sc.contains(event)
            if cont:
                self.update_annot(ind)
                self.annot.set_visible(True)
                self.fig.canvas.draw_idle()
            else:
                if vis:
                    self.annot.set_visible(False)
                    self.fig.canvas.draw_idle()

    def plot(self, xvalues, yvalues, xerr, yerr, colors, names, spec, los, hover):
        self.names = names
        self.c = colors

        self.min  =min(colors)
        self.max = max(colors)
        print self.min, self.max
        self.sc = plt.scatter(xvalues, yvalues, c=colors,  s =100, cmap=self.cmap, norm=self.norm)
        _, __ ,errorlinecollection = plt.errorbar(xvalues, yvalues, xerr = xerr, yerr = yerr, marker='', ls='', zorder=0)
        #cb = plt.colorbar.ColorbarBase(cax, cmap=cmap, norm=normalize)
        cb = plt.colorbar()
        error_color = cb.to_rgba(colors)

        errorlinecollection[0].set_color(error_color)
        errorlinecollection[1].set_color(error_color)


        #self.eb = plt.errorbar(xvalues, yvalues, xerr= xerr, yerr= yerr,  fmt = '', ecolor =colors)
        self.fig.canvas.mpl_connect("motion_notify_event", self.hover)

        plt.title(str(spec)+ '_' + str(los))
        cb.set_label('Nitrogen intensity')
        plt.axvline(x=0.0, color='grey', linestyle='-')
        plt.axhline(y=0.0, color='grey', linestyle='-')
        plt.xlabel('Divertor Temperature [eV]')
        plt.ylabel('Velocity [km/s]')
        plt.minorticks_on()
        plt.grid(which= 'both', axis = 'x')
        plt.grid(which= 'major`', axis = 'y')

        ax= plt.gca()
        plt.show()


    def plot2(self, xvalues, yvalues, xerr, yerr, colors, names, spec, los, hovers):
        self.hovers = hovers
        self.names = names
        self.c = colors

        self.min  =min(colors)
        self.max = max(colors)
        print self.min, self.max
        self.sc = plt.scatter(xvalues, yvalues, c=colors,  s =100, cmap=self.cmap2, norm=self.norm)
        _, __ ,errorlinecollection = plt.errorbar(xvalues, yvalues, xerr = xerr, yerr = yerr, marker='', ls='', zorder=0)

        cb = plt.colorbar()
        error_color = cb.to_rgba(colors)

        errorlinecollection[0].set_color(error_color)
        errorlinecollection[1].set_color(error_color)

        self.fig.canvas.mpl_connect("motion_notify_event", self.doHovers)

        plt.title(str(spec)+ '_' + str(los))
        cb.set_label(self.label)
        plt.axvline(x=0.0, color='grey', linestyle='-')
        plt.axhline(y=0.0, color='grey', linestyle='-')
        plt.xlabel('Divertor Temperature [eV]')
        plt.ylabel('Velocity [km/s]')
        plt.minorticks_on()
        plt.grid(which= 'both', axis = 'x')
        plt.grid(which= 'major`', axis = 'y')

        ax= plt.gca()
        #plt.show()
