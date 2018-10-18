from multiprocessing import Pool
import cpu_adapter
import sys
import json
sys.path.append('mem')
import mem_experiment

sys.path.append('cpu')
import cpu_experiment

sys.path.append('disk')
import disk_experiment
from flask import Flask, request, abort

finalUtilityCpu =0.0
finalutilityDisk =0.0
finalutilityOfmem =0.0
maxU={'metric':'','value':0.0, 'swarmed':False, 'adapted': False, 'msg':''}
result_adapt={}

app = Flask(__name__)
swarmed=maxU['swarmed']
adapted=maxU['adapted']
def runInParallel(*fns):
  proc = []
  for fn in fns:
    p = Process(target=fn)
    p.start()
    proc.append(p)
  for p in proc:
    p.join()


 


def run_swarm():
	if maxU['swarmed'] == False:
		pool = Pool(processes=3)              # Start a worker processes.
		result = pool.apply_async(disk_experiment.run_disk_experiment)
		result1 = pool.apply_async(cpu_experiment.run_cpu_experiment)
		result2 = pool.apply_async(mem_experiment.run_mem_experiment)
		print result.get(timeout=7600), result1.get(timeout=7600), result2.get(timeout=7600)
	 
		#disk_experiment.run_disk_experiment()
		#cpu_experiment.run_cpu_experiment()
		#mem_experiment.run_mem_experiment()
		#runInParallel(disk_experiment.run_disk_experiment(), cpu_experiment.run_cpu_experiment(), mem_experiment.run_mem_experiment())
		print "swarm finished "
		maxU['swarmed'] =True
		maxU['msg'] ='swarm finished'
	else:
		print "No need to swarm  already done"
		maxU['msg'] ='No need to swarm  already done'

	return True

def callback():
	return "swarm finished in subprocess "
@app.route('/')
def hi():
	swarmed=maxU['swarmed']
	print 'swarmed', swarmed
	if swarmed==False:

		print "no swarm found !"
		
		swarmed= run_swarm()
		maxU['swarmed'] = swarmed
	elif swarmed==True: 
		 maxU['swarmed'] = True
		 maxU['msg'] ="No need to swarm"

	

	return json.dumps(maxU)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
    	'''
    	swarmed=maxU['swarmed']
    	pool = Pool(processes=1)
    	result = pool.apply_async(cpu_adapter.run, () , callback)
    	print 'result_adapt: ', result
    	'''
        print(request.json)
        sleep(20)
        return '', 200
    else:
        abort(400)




if __name__ == '__main__':
	app.run(host='0.0.0.0', port='8888')

 


 