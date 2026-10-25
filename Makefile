.PHONY: test demo compare preview clean

test:
	python3 -m unittest discover -s tests -v

demo:
	python3 -m a2l build examples/two_stage/two_stage.sp --out examples/two_stage/out --area-budget-mm2 0.005 --fail-on-gate

compare:
	python3 -m a2l compare examples/ota5/ota5.sp examples/ota5_cascode/ota5_cascode.sp --out out/compare

preview: demo
	PYTHONPATH=.tools python3 -c "import cairosvg; cairosvg.svg2png(url='examples/two_stage/out/floorplan.svg', write_to='out/floorplan_preview.png', scale=2)"

clean:
	rm -rf out __pycache__ a2l/__pycache__ tests/__pycache__
