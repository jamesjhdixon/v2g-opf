#==================================================================
# printout.py
# A Python script to write output to xls and on screen
# ---Author---
# W. Bukhsh,
# wbukhsh@gmail.com
# OATS
# Copyright (c) 2015 by W Bukhsh, Glasgow, Scotland
# OATS is distributed under the GNU GENERAL PUBLIC LICENSE v3 (see LICENSE file for details).
#==================================================================
from pyomo.opt import SolverStatus, TerminationCondition
from tabulate import tabulate
import pandas as pd
import math
import sys
class printoutput(object):
    def __init__(self, results, instance,mod):
        self.results   = results
        self.instance  = instance
        self.mod       = mod
    def greet(self):
        print ("========================")
        print ("\n Output from the OATS")
        print ("========================")
    def solutionstatus(self):
        self.instance.solutions.load_from(self.results)
        print ("------Solver Message------")
        print (self.results.solver)
        print ("--------------------------")
        if (self.results.solver.status == SolverStatus.ok) \
        and (self.results.solver.termination_condition == TerminationCondition.optimal):
            print ("Optimization Converged!")
        elif self.results.solver.termination_condition == TerminationCondition.infeasible:
            sys.exit("Problem is infeasible!\nOats terminated. No output is written on the results file.")
        else:
            print (sys.exit("Problem is infeasible!\nOats terminated. No output is written on the results file."))
    def printsummary(self):
        if 'LF' not in self.mod:
            print ("Cost of the objective function:", str(float(self.instance.OBJ())))
        print ("***********")
        print ("\n Summary")
        print ("***********")
        tab_summary = []
        tab_summary.append(['Time period','Conventional generation (kW)', 'Demand (kW)','Objective function value'])
        for t in self.instance.T:
            tab_summary.append([t,sum(self.instance.pG[g,t].value for g in self.instance.G)*self.instance.baseMVA,\
            sum(self.instance.PD[d,t] for d in self.instance.D)*self.instance.baseMVA, self.instance.CostTP[t].value])
        print (tabulate(tab_summary, headers="firstrow", tablefmt="grid"))
        print ("==============================================")

        # ev_summary = []
        # ev_summary.append(['Time period','Window','EV', 'Charging','SoC'])

        # for (ev,w,t) in self.instance.FlexTimes:
        #     ev_summary.append([t,w,ev,self.instance.pEV[ev,w,t].value,self.instance.SoC[ev,w,t].value])
        # print tabulate(ev_summary, headers="firstrow", tablefmt="grid")
        # print "=============================================="
    def printoutputxls(self):
        #===initialise pandas dataframes
        cols_summary    = ['Time period','Conventional generation (kW)', 'Demand (kW)','Objective function value']
        cols_bus        = ['Time period','name', 'angle(degs)']
        cols_demand     = ['Time period','name', 'busname', 'PD(kW)','alpha']

        cols_branch     = ['Time period','name', 'from_busname', 'to_busname', 'pL(kW)','SLmax(kW)']
        cols_transf     = ['Time period','name', 'from_busname', 'to_busname', 'pLT(kW)','SLmax(kW)']
        cols_generation = ['Time period','name', 'busname', 'PGLB(kW)', 'pG(kW)','PGUB(kW)']
        cols_EVs        = ['Time period','name','Window','Charging(kW)','Discharging(kW)','SoC(kWh)']

        summary         = pd.DataFrame(columns=cols_summary)
        bus             = pd.DataFrame(columns=cols_bus)
        demand          = pd.DataFrame(columns=cols_demand)
        generation      = pd.DataFrame(columns=cols_generation)
        branch          = pd.DataFrame(columns=cols_branch)
        transformer     = pd.DataFrame(columns=cols_transf)
        EV             = pd.DataFrame(columns=cols_EVs)

        #-----write Data Frames
        #summary
        ind = 0
        for t in self.instance.T:
            summary.loc[ind] = pd.Series({'Time period':t,'Conventional generation (kW)': sum(self.instance.pG[g,t].value for g in self.instance.G)*self.instance.baseMVA,\
        'Demand (kW)':sum(self.instance.PD[d,t] for d in self.instance.D)*self.instance.baseMVA,\
        'Objective function value': self.instance.CostTP[t].value})
            ind += 1
        #bus data
        ind=0
        for t in self.instance.T:
            for b in self.instance.B:
                bus.loc[ind] = pd.Series({'Time period':t,'name': b,'angle(degs)':self.instance.delta[b,t].value*180/math.pi})
                ind += 1
        #line data
        ind=0
        for t in self.instance.T:
            for b in self.instance.L:
                branch.loc[ind] = pd.Series({'Time period':t,'name': b, 'from_busname':self.instance.A[b,1], 'to_busname':self.instance.A[b,2],\
                'pL(kW)':self.instance.pL[b,t].value*self.instance.baseMVA,'SLmax(kW)':self.instance.SLmax[b]*self.instance.baseMVA})
                ind += 1
        #transformer data
        ind = 0
        for t in self.instance.T:
            for b in self.instance.TRANSF:
                transformer.loc[ind] = pd.Series({'Time period':t,'name': b, 'from_busname':self.instance.AT[b,1],\
                'to_busname':self.instance.AT[b,2], 'pLT(kW)':self.instance.pLT[b,t].value*self.instance.baseMVA,\
                'SLmax(kW)':self.instance.SLmaxT[b]*self.instance.baseMVA})
                ind += 1
        #demand data
        ind = 0
        for t in self.instance.T:
            for d in self.instance.Dbs:
                demand.loc[ind] = pd.Series({'Time period':t,'name': d[1],'busname':d[0],'PD(kW)':self.instance.PD[d[1],t]*self.instance.baseMVA,\
                'alpha':round(self.instance.alpha[d[1],t].value,3)})
                ind += 1
        #generator data
        ind = 0
        for t in self.instance.T:
            for g in self.instance.Gbs:
                generation.loc[ind] = pd.Series({'Time period':t,'name':g[0], 'busname':g[1],\
                'PGLB(kW)':self.instance.PGmin[g[1]]*self.instance.baseMVA,\
                'pG(kW)':round(self.instance.pG[g[1],t].value*self.instance.baseMVA,3),\
                'PGUB(kW)':self.instance.PGmax[g[1]]*self.instance.baseMVA})
                ind += 1
        #EVs data
        ind = 0
        for (ev,w,t) in self.instance.FlexTimes:
            EV.loc[ind] = pd.Series({'Time period':t,'name':ev,\
                'Window':w,'Charging(kW)':self.instance.pEV[ev,w,t].value,\
                'Discharging(kW)':self.instance.dEV[ev,w,t].value,\
                'SoC(kWh)':self.instance.SoC[ev,w,t].value})
            ind += 1


        #----------------------------------------------------------
        #===write output on xlsx file===
        #
        bus = bus.sort_values(['name'])
        EV  = EV.sort_values(['name','Time period'])
        generation = generation.sort_values(['name'])
        demand = demand.sort_values(['name'])
        writer = pd.ExcelWriter('results/results.xlsx', engine ='xlsxwriter')
        summary.to_excel(writer, sheet_name = 'summary',index=False)
        bus.to_excel(writer, sheet_name = 'bus',index=False)
        demand.to_excel(writer, sheet_name = 'demand',index=False)
        generation.to_excel(writer, sheet_name = 'generator',index=False)
        branch.to_excel(writer, sheet_name = 'branch',index=False)
        transformer.to_excel(writer, sheet_name = 'transformer',index=False)
        EV.to_excel(writer, sheet_name = 'EVs',index=False)
        writer.save()
