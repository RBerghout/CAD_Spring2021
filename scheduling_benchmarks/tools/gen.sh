for VARIABLE in {1..10}
do
	python generate_graphs.py rand_DFG_s10_${VARIABLE}.edgelist 10
	python generate_graphs.py rand_DFG_s50_${VARIABLE}.edgelist 50
done
