
import plotly.graph_objects as go

# Define the comparison data
aspects = [
    "Access Method",
    "Execution Model",
    "Best Use Cases",
    "Advantages",
    "Disadvantages",
    "Response Time",
    "Suitable For",
    "Example Scenario"
]

standalone = [
    "Direct Python import & function calls",
    "Synchronous - blocks until complete",
    "Scripts, automation, local processing",
    "Simple setup, direct control, no server overhead",
    "No remote access, blocks execution, single-threaded",
    "Immediate but blocking",
    "Local scripts, batch jobs, CLI tools",
    "Daily report generation script"
]

fastapi = [
    "HTTP REST API endpoints",
    "Asynchronous - background tasks with status tracking",
    "Web apps, remote access, concurrent requests",
    "Remote access, non-blocking, scalable, multiple users",
    "Server setup required, network latency, more complex",
    "Delayed but non-blocking",
    "Web services, multi-user apps, distributed systems",
    "Web dashboard with multiple users"
]

# Create the table
fig = go.Figure(data=[go.Table(
    columnwidth=[1.2, 2, 2],
    header=dict(
        values=['<b>Aspect</b>', '<b>Standalone Module</b>', '<b>FastAPI App</b>'],
        fill_color='#1FB8CD',
        align='left',
        font=dict(color='white', size=13),
        height=40
    ),
    cells=dict(
        values=[aspects, standalone, fastapi],
        fill_color=[['#f9f9f9', 'white']*4],
        align='left',
        font=dict(size=11),
        height=50
    )
)])

fig.update_layout(
    title="Standalone vs FastAPI Comparison"
)

# Save as PNG and SVG
fig.write_image("comparison_table.png")
fig.write_image("comparison_table.svg", format="svg")
