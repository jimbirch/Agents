# Agents

A collection of spatially-explicit agent-based models for animal movement, written in Fortran and Python.

Current Models:
- model.f90 — A very basic random walk model and the framework for other models. Change the coordinates and swim speed to something appropriate and the agent will change direction and move at its swim speed in that direction at a constant speed every second for two weeks, unconstrained by geography or flow. Direction changes are randomly chosen between 90° to the left or right of the current heading. This can be adjusted by multiplying deltad by a constant prior to adding it to direction.
- flowmodel.f90 — The same as model.f90 but with a very simple implementation of water current. The agent's direction and swim speed is added to a vector representing the speed and direction of a current. Agents still adjust their swim direction up to 90° to the left or right and swim at a constant speed.
- boid.py — a spatially explicit boids model being developed for use in a QGIS plugin.
