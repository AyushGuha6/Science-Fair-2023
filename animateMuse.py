from matplotlib import pyplot as plt, style, animation
import numpy as np

class Graph():
    def __init__(self) -> None:
        self.delta ,self.theta, self.alpha, self.beta, self.gamma, self.ppg_red, self.ppg_ir, self.gsr= 0
        
        plt.style.use("bmh")
        self.fig, ((self.ax1, self.ax2),(self.ax3, self.ax4)) = plt.subplots(2,2, figsize=(8,6))
     
        self.x = []
        self.delta_ax1_y1 = []
        self.theta_ax1_y1 = []
        self.alpha_ax1_y1 = []
        self.beta_ax1_y1  = []
        self.gamma_ax1_y1 = []

        self.counter=0
        #ax1.set_ylabel('ohms')

        self.ax2_y = []
        #self.ppg_red_ax3_y = []
        self.ppg_ir_ax3_y = []
        self.ax4_y = []

    def animate(self,i,eegfile,ppgrawfile):
        #plt.cla()
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()
        self.ax4.clear()
        
        self.ax1.set_title('EEG Bands')
        self.ax2.set_title('Beta/Alpha')
        self.ax3.set_title('PPG RED')
        self.ax4.set_title('GSR')

        self.x.append(self.counter)
        self.delta, self.theta, self.alpha, self.beta, self.gamma = self.EEGLastNLines(eegfile, 10)
        self.ppg_red, self.ppg_ir = self.PPGRawLastNLines(ppgrawfile, 10)
        #y.append(gsr_data)
        #print("Called read file...")
        #print(f'Delta:{self.delta},Theta:{self.theta}')
        self.delta_ax1_y1.append(round(self.delta,2))
        self.theta_ax1_y1.append(round(self.theta,2))
        self.alpha_ax1_y1.append(round(self.alpha,2))
        self.beta_ax1_y1.append(round(self.beta,2))
        self.gamma_ax1_y1.append(round(self.gamma,2))

        self.ax2_y.append(round(self.beta/self.alpha,2))
        #self.ppg_red_ax3_y.append(round(self.ppg_red,2)) ## PPG
        self.ppg_ir_ax3_y.append(round(self.ppg_ir,2))
        self.ax4_y.append(self.gsr) ## GSR

        self.ax1.set_xlim(self.counter-20,self.counter)
        self.ax2.set_xlim(self.counter-20,self.counter)
        self.ax3.set_xlim(self.counter-20,self.counter)
        self.ax4.set_xlim(self.counter-20,self.counter)
        #self.ax1.set_ylim(200,20000)
        #self.ax2.set_ylim(0,10)
        #self.ax3.set_ylim(200,1200)
        #self.ax4.set_ylim(5,600)

        #self.ax1.plot(self.x,self.delta_ax1_y1,'tab:orange', label='Delta')
        #self.ax1.plot(self.x,self.theta_ax1_y1,'tab:blue', label='Theta')
        self.ax1.plot(self.x,self.alpha_ax1_y1,'tab:olive', label='Alpha')
        self.ax1.plot(self.x,self.beta_ax1_y1,'tab:cyan', label='Beta')
        #self.ax1.plot(self.x,self.gamma_ax1_y1,'tab:green', label='Gamma')

        self.ax2.plot(self.x,self.ax2_y, 'tab:blue', label='Beta/Alpha') 
        #self.ax3.plot(self.x,self.ppg_red_ax3_y, 'tab:green', label='PPG Red') 
        self.ax3.plot(self.x,self.ppg_ir_ax3_y, 'tab:orange', label='PPG IR')
        self.ax4.plot(self.x,self.ax4_y, 'tab:red', label = 'GSR') 

        self.ax1.legend(loc='upper right', fontsize='small')
        self.ax2.legend(loc='upper right', fontsize='small')
        self.ax2.get_legend().texts[0].set_text(round(self.beta/self.alpha,2))
        self.ax3.legend(loc='upper right', fontsize='small')
        self.fig.tight_layout()

        self.counter += 1

    def EEGLastNLines(self,f,n):
        delta = []
        theta = []
        alpha = []
        beta  = []
        gamma = []

        with open(f) as file:
            for line in (file.readlines()[-n:]):
                x = line.split(',')
                if str(x[0]) != "TIME":
                    delta.append(float(str(x[1]))) 
                    theta.append(float(str(x[2])))
                    alpha.append(float(str(x[3])))
                    beta.append(float(str(x[4])))
                    gamma.append(float(str(x[5]).replace('\n','')))
            return np.around(np.mean(np.array(delta))), \
                np.around(np.mean(np.array(theta))), \
                np.around(np.mean(np.array(alpha))), \
                np.around(np.mean(np.array(beta))), \
                np.around(np.mean(np.array(gamma)))
    
    def PPGRawLastNLines(self,f,n):
        #hr = []
        ppg_red = []
        ppg_ir = []

        with open(f) as file:
            for line in (file.readlines()[-n:]):
                x = line.split('\t')
                ppg_red.append(float(str(x[1]))) 
                ppg_ir.append(float(str(x[2])))
            #print(np.around(np.mean(np.array(ppg_red))))
            return np.around(np.mean(np.array(ppg_red))),np.around(np.mean(np.array(ppg_ir)))
        
    def PPGLastNLines(self,f,n):
        hr = []

        with open(f) as file:
            for line in (file.readlines()[-n:]):
                x = line.split('\t')
                hr.append(float(str(x[1]))) 
            print(np.around(np.mean(np.array(hr))))
            return np.around(np.mean(np.array(hr)))

def main():
    g1 = Graph()
    anim = animation.FuncAnimation(g1.fig, g1.animate, interval=1000, frames=100) 
    plt.show()
    plt.close()
if __name__ == '__main__':
    main()