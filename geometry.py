# -*- coding: cp936 -*-
import numpy as np
class CNode:
    ID=0
    coord=np.array([0,0,0])
    def __init__(self):
        self.ID=0
        self.coord=np.array([0,0,0])
        self.restrain=np.array([0,0,0])
        self.MID=0
        self.CID=1
    def __str__(self):
        return str(self.ID)+'--'+str(self.coord)
        
class CElement:
    ID = 0
    MID=0
    CID=0
    TOPO=np.array([])
    Mele=[]
    def __init_(self):
        pass
    def __str__(self):
        return str([self.ID]+list(self.TOPO)+[self.CID,self.MID])

class CMesh(object):
    nodenum=0
    elenum=0
    node=[]
    element=[]
    def __init__(self):
    	self.nodenum=0
    	self.elenum=0
    	self.node=[]
    	self.element=[]
    
    def nodeIn(self,filename):
        with open(filename,'r') as f:
            lines = f.readlines()
            del lines[0]
            self.nodenum=len(lines)
            for i in range(self.nodenum):                
                self.node.append(CNode())
                self.node[i].ID = int(lines[i].split()[0])
                self.node[i].coord=list(map(float,lines[i].split()[1:4]))
    def elementIn(self,filename):
        with open(filename,'r') as f:
            lines = f.readlines()
            del lines[0]
            self.elenum=len(lines)
            for i in range(self.elenum):                
                self.element.append(CElement())
                self.element[i].ID = int(lines[i].split()[0])
                self.element[i].TOPO=np.array(map(int,lines[i].split()[4:13]))
    def meshIn(self,filename):
        with open(filename,'r') as f:
            line = f.readline()
            self.nodenum, self.elenum=map(int,line.split()[0:2])
            for i in range(self.nodenum):
                line=f.readline()
                self.node.append(CNode())
                self.node[i].ID = int(line.split()[0])
                self.node[i].restrain=list(map(int,line.split()[1:4]))
                self.node[i].coord=list(map(float,line.split()[4:7]))
            for i in range(self.elenum):
                line=f.readline()
                self.element.append(CElement())
                self.element[i].ID = int(line.split()[0])
                self.element[i].TOPO=np.array(map(int,line.split()[1:9]))
                self.element[i].MID,self.element[i].CID=map(int,line.split()[9:11])

    def nodeContanaOut(self,filename):
        with open(filename,'w') as f:
            f.write('#x y z \n')
            for node in self.node:
                line=str([node.ID])[1:-1]+' '+str(node.coord).replace(',',' ')[1:-1]+' '\
                        +str([node.MID,node.CID]).replace(',',' ')[1:-1]
                f.write(str(line)+'\n')
    def eleContanaOut(self,filename):
        with open(filename,'w') as f:
            f.write(' # EID MeleID  MatID   RebarID Connect\n')
            for ele in self.element:
                line=[ele.ID]+[4,ele.MID,0]+list(ele.TOPO)
                f.write(str(line).replace(',',' ')[1:-1]+'\n')

    def tecplotOut(self,filename="MeshTec.dat",title="Mesh"):
        with open(filename,'a+') as f:
            f.write('TITLE='+title+'\n')
            f.write('VARATBLES=X,Y,Z \n')
            line='ZONE N= '+str(self.nodenum)+ ',E='+str(self.elenum ) + ',DATAPACKING=POINT,ZONETYPE=FEBRICK'
            f.write(line+'\n')
            for node in self.node:
                f.write(str(node.coord)[1:-1]+'\n')
            for ele in self.element:
                f.write(str(ele.TOPO)[1:-1]+'\n')


class CSegment:
    def __init__(self):
        self.SID=0
        self.EID=0
        self.FID=0
        self.TOPO=[]
        self.center=np.array([])
    def __str__(self):
        return str([self.SID,self.EID,self.FID])
    def geneTopo(self,mesh):
        FaceTopo=np.array([[1,2,3,4],[2,1,5,6],[3,2,6,7],[4,3,7,8],[1,4,8,5],[8,7,6,5]])
        self.TOPO = mesh.element[self.EID-1].TOPO[FaceTopo[self.FID-1,:]-1]

class CSurface:
    def __init__(self):
        self.SID=0
        self.segNum=0
        self.DefProp=1  #1:deformable
        self.segList=[]
        self.center=np.array([])
        self.coordRange=np.array([])
    def surfaceIN(self,lines):
        pass
    def __str__(self):
        result='**  SurfaceID   FENum   DefProp  **\n'
        result= result+str([self.SID,self.segNum,self.DefProp]).replace('[',' ').replace(']',' ').replace(',',' ')+'\n'
        result += '**   SegmnetID   EID FID  **\n'
        for seg in self.segList:
            result += str(seg).replace('[',' ').replace(']',' ').replace(',',' ')+'\n'
        return str(result)

    
    def tecplotOut(self,mesh=CMesh(),filename="surface.dat"):
        nodelist=list()
        for seg in self.segList:
            nodelist.extend(seg.TOPO)
        nodelist=list(set(nodelist))
        nodelist.sort()
        with open(filename,'a+') as f:
            line='ZONE N= '+str(len(nodelist))+ ',E='+str(self.segNum )+',ZONETYPE=FEQuadrilateral,DATAPACKING=POINT'
            f.write(line+'\n')
            for NID in nodelist:
                for x in mesh.node[NID-1].coord:
                    f.write(str(x)+'   ')
                f.write('\n')
            for seg in self.segList:
                for NID in seg.TOPO:
                    f.write(str(nodelist.index(NID)+1)+'  ')
                f.write('\n')

class CBody(object):
    mesh=CMesh()
    surfNum=0
    surfList=[]
    def surfaceListIN(self,filename,mode=0):
        #mode=0:Contana format
        with open(filename,'r') as f:
            if mode==0:
                for i in range(self.surfNum):
                    self.surfList.append(CSurface())
                    surf=self.surfList[i]
                    surf.segList=[]
                    f.readline()
                    surf.SID,surf.segNum,surf.DefProp=map(int,f.readline().split())
                    f.readline()
                    for j in range(surf.segNum):
                        surf.segList.append(CSegment())
                        seg=surf.segList[-1]
                        seg.SID,seg.EID,seg.FID = map(int,f.readline().split())
            elif mode==1:   #txt format
                self.surfNum=int(f.readline())
                for i in range(self.surfNum):
                    self.surfList.append(CSurface())
                    surf=self.surfList[i]
                    surf.SID=i+1
                    surf.segList=[]
                    surf.segNum=int(f.readline())
                    for j in range(surf.segNum):
                        surf.segList.append(CSegment())
                        seg=surf.segList[-1]
                        seg.SID,seg.EID,seg.FID = map(int,f.readline().split())
    def surfListOut(self,filename,mode=0):
        with open(filename,'w') as f:
            if mode==0:     #Contana format
                for surf in self.surfList:
                    f.write(str(surf))




