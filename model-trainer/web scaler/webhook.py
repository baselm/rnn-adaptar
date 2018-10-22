from flask import Flask, request, abort
import cpu_experiment

app = Flask(__name__)
@app.route('/')
def hi():
	return "<h1> Hi Welcome to Adaptation Manager"

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        print(request.json)
        runInParallel(run_cpu_experiment, run_mem_experiment )
        return '', 200
    else:
        abort(400)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='8888', debug=True)