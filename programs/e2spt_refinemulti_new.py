#!/usr/bin/env python
# Muyuan Chen 2021-04
from EMAN2 import *
import numpy as np
from e2spt_refine_new import gather_metadata

def main():
	
	usage="Pass references as direct arguments (no --)"
	parser = EMArgumentParser(usage=usage,version=EMANVERSION)
	parser.add_argument("--ptcls", type=str,help="path", default=None)
	parser.add_argument("--path", type=str,help="path", default=None)
	parser.add_argument("--nref", type=int,help="duplicate the first ref N times with phase randomization at 2xres", default=-1)
	parser.add_argument("--maskalign", type=str,default=None,help="Mask file applied to 3D alignment reference in each iteration. Not applied to the average, which will follow normal masking routine.")
	parser.add_argument("--maxres",type=float,help="Maximum resolution (the smaller number) to consider in alignment (in A, not 1/A)",default=0)
	parser.add_argument("--minres",type=float,help="Minimum resolution (the larger number) to consider in alignment (in A, not 1/A)",default=0)
	parser.add_argument("--niter", type=int,help="number of iterations", default=5)
	parser.add_argument("--loadali3d",help="load previous 3d alignment from --ptcls input.",action="store_true",default=False)
	parser.add_argument("--res", type=float,help="target resolution", default=20.)
	parser.add_argument("--skipali",action="store_true",help=".",default=False)
	parser.add_argument("--threads", type=int,help="", default=12)
	parser.add_argument("--parallel", type=str,help="parallel", default="thread:12")
	parser.add_argument("--sym", type=str,help="symmetry to apply to the average structure", default="c1")
	parser.add_argument("--breaksym", type=str,help="break specified symmetry", default=None)
	parser.add_argument("--setsf", type=str,help="set structure factor", default=None)

	(options, args) = parser.parse_args()
	logid=E2init(sys.argv)

	if options.path==None: options.path=num_path_new("sptcls_")
	path=options.path
	print(f"Writing in {path}...")
	
	info2dname=f"{path}/particle_info_2d.lst"
	info3dname=f"{path}/particle_info_3d.lst"
	
	if os.path.isfile(info2dname) and os.path.isfile(info3dname):
		print("Using existing metadata files within the directory...")
		info2d=load_lst_params(info2dname)
		info3d=load_lst_params(info3dname)
		
	else:
		info2d, info3d = gather_metadata(options.ptcls)
		save_lst_params(info3d, info3dname)
		save_lst_params(info2d, info2dname)
		
	ep=EMData(info3dname,0,True)
	boxsize=ep["ny"]
	p2=EMData(info2dname,0,True)
	padsize=p2["ny"]
		
	if options.maskalign!=None: options.maskalign=EMData(options.maskalign)
	if options.setsf!=None:
		setsf=" --setsf {}".format(options.setsf)
	else:
		setsf=""

	options.cmd=' '.join(sys.argv)
	fm=f"{path}/0_spt_params.json"
	js=js_open_dict(fm)
	js.update(vars(options))
	js.close()
	
	if options.loadali3d and options.nref>0:
		print("Generating initial references by random classification...")
		nref=options.nref
		ali3d=load_lst_params(options.ptcls)
		ali2d,ali3d=classify_ptcls(ali3d, info2d, options)
		save_lst_params(ali2d, f"{path}/aliptcls2d_00.lst")
		save_lst_params(ali3d, f"{path}/aliptcls3d_00.lst")
		options.ptcls=f"{path}/aliptcls3d_00.lst"
		for i in range(options.nref):
			threed=f"{path}/threed_00_{i:02d}.hdf"
			run(f"e2spa_make3d.py --input {path}/aliptcls2d_00.lst --output {threed} --keep 1 --parallel thread:{options.threads} --outsize {boxsize} --pad {padsize} --sym {options.sym} --clsid {i}")
			run(f"e2proc3d.py {threed} {threed} {setsf} --process filter.lowpass.gauss:cutoff_freq={1./options.res} --process normalize.edgemean")
	else:
		print("Loading references...")
		if options.nref>0:
			r=EMData(args[0])
			nref=options.nref
			refs=[]
			for i in range(nref):
				e=r.process("filter.lowpass.randomphase",{"cutoff_freq":1./(options.res*2)})
				refs.append(e)
		else:
			refs=[EMData(a) for a in args]
			nref=len(refs)
			
		for i,r in enumerate(refs):
			r.write_image(f"{path}/threed_00_{i:02d}.hdf")
		
		
	opt=""
	if options.skipali:
		opt+=" --skipali"
		
	if options.loadali3d:
		ptcls=options.ptcls
	else:
		ptcls=info3dname
		opt+=" --fromscratch"
	if options.breaksym!=None:
		opt+=" --breaksym {}".format(options.breaksym)
		
	if options.minres>0: opt+=f" --minres {options.minres}"
	if options.maxres>0: opt+=f" --maxres {options.maxres}"
		
	for itr in range(1,1+options.niter):
		ali2d=[]
		ali3d=[]
		
		for ir in range(nref):
			oref=f"{path}/threed_{itr-1:02d}_{ir:02d}.hdf"
			ref=f"{path}/aliref_{ir:02d}.hdf"		# overwrite each iteration

			modref=EMData(oref)
			if options.maskalign!=None: 
				# These initial filters are to reduce the artifacts produced by masking
				if options.maxres>0: modref.process_inplace("filter.lowpass.gauss",{"cutoff_freq":1.0/options.maxres})
				if options.minres>0: modref.process_inplace("filter.highpass.gauss",{"cutoff_freq":1.0/options.minres})
				modref.mult(options.maskalign)
			modref.write_compressed(ref,0,12,erase=True)
			
			run(f"e2spt_align_subtlt.py {ptcls} {ref} --path {path} --iter {itr} --maxres {options.res:.2f} --parallel {options.parallel} {opt}")
			
			ali2d.append(f"{path}/aliptcls2d_{itr:02d}_{ir:02d}.lst")
			os.rename(f"{path}/aliptcls2d_{itr:02d}.lst", ali2d[-1])
			ali3d.append(f"{path}/aliptcls3d_{itr:02d}_{ir:02d}.lst")
			os.rename(f"{path}/aliptcls3d_{itr:02d}.lst", ali3d[-1])
		
		ali3dpms=[load_lst_params(a) for a in ali3d]
		ali2dpms=[load_lst_params(a) for a in ali2d]
		score=[]
		for ali in ali3dpms:
			scr=[a["score"] for a in ali]
			score.append(scr)
		score=np.array(score)
		clsid=np.argmin(score, axis=0)
		for i in np.unique(clsid):
			print("  class {} - {} particles".format(i, np.sum(clsid==i)))
		
		for ia,ali in enumerate(ali3dpms):
			for i,a in enumerate(ali):
				a["class"]=clsid[i]
				idx=info3d[i]["idx2d"]
				for x in idx:
					ali2dpms[ia][x]["class"]=clsid[i]
			
			ali3dpms[ia]=[a for a in ali if a["class"]==ia]
					
		for i in range(nref):
			save_lst_params(ali2dpms[i], ali2d[i])
			save_lst_params(ali3dpms[i], ali3d[i])
		
		
		for ir in range(nref):
			threed=f"{path}/threed_{itr:02d}_{ir:02d}.hdf"
			a2=ali2d[ir]
			run(f"e2spa_make3d.py --input {a2} --output {threed} --keep 1 --parallel thread:{options.threads} --outsize {boxsize} --pad {padsize} --sym {options.sym} --clsid {ir}")
			
			run(f"e2proc3d.py {threed} {threed} {setsf} --process filter.lowpass.gauss:cutoff_freq={1./options.res} --process normalize.edgemean")
		

	E2end(logid)
	
def classify_ptcls(ali3d, info2d, options):
	ali2d=[]
	cls=np.arange(len(ali3d))%options.nref
	np.random.shuffle(cls)
	if options.breaksym!=None:
		xf=Transform()
		nsym=xf.get_nsym(options.breaksym)
		symidx=np.arange(len(ali3d))%nsym
		np.random.shuffle(symidx)
		for i,a in enumerate(ali3d):
			xf3d=a["xform.align3d"].inverse()
			xf3d=xf3d.get_sym(options.breaksym, int(symidx[i]))
			a["xform.align3d"]=xf3d.inverse()
		
	for p in info2d:
		pid=p["idx3d"]
		a={"src":p["src"], "idx":p["idx"],
			"tilt_id":p["tilt_id"], "ptcl3d_id":pid, "score":-1}
		xf3d=ali3d[pid]["xform.align3d"].inverse()
		
		pjxf=p["xform.projection"]*xf3d
		a["xform.projection"]=pjxf
		a["class"]=cls[pid]
		ali2d.append(a)
		
	return ali2d,ali3d
	
	
def run(cmd):
	print(cmd)
	launch_childprocess(cmd)

if __name__ == '__main__':
	main()
	