import sabase2
sabase2.set_device()
f,x = sabase2.gettraceSA()
diff =  len(f) - len(x)
if diff > 0:
    f = f[:-diff]
sabase2.plottraceSA(f,x,plttitle="mytitle")
