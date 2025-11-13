
import plotly.graph_objects as go

# Create a comprehensive architecture diagram using Plotly shapes and annotations
fig = go.Figure()

# Define positions for each layer (y-coordinates)
client_y = 3.5
core_y = 2.5
processing_y = 1.5
output_y = 0.5

# Define x positions for components in each layer
# Client Layer (3 components)
client_x = [1, 2.5, 4]
# Core Layer (3 components)
core_x = [1, 2.5, 4]
# Processing Layer (6 components in 2 rows)
processing_x = [0.5, 2, 3.5, 0.5, 2, 3.5]
processing_y_vals = [1.7, 1.7, 1.7, 1.3, 1.3, 1.3]
# Output Layer (3 components)
output_x = [1, 2.5, 4]

# Client Layer boxes
client_labels = ['Python Script', 'FastAPI REST', 'CLI Interface']
client_colors = ['#B3E5EC', '#B3E5EC', '#B3E5EC']

for i, (x, label) in enumerate(zip(client_x, client_labels)):
    fig.add_shape(type="rect", x0=x-0.4, y0=client_y-0.15, x1=x+0.4, y1=client_y+0.15,
                  line=dict(color="#21808d", width=2), fillcolor=client_colors[i])
    fig.add_annotation(x=x, y=client_y, text=label, showarrow=False, 
                       font=dict(size=11, color="#13343b"))

# Core Layer boxes
core_labels = ['zai_reader.py', 'DocumentReader', 'FastAPI app.py']
core_colors = ['#A5D6A7', '#A5D6A7', '#A5D6A7']

for i, (x, label) in enumerate(zip(core_x, core_labels)):
    fig.add_shape(type="rect", x0=x-0.4, y0=core_y-0.15, x1=x+0.4, y1=core_y+0.15,
                  line=dict(color="#2E8B57", width=2), fillcolor=core_colors[i])
    fig.add_annotation(x=x, y=core_y, text=label, showarrow=False,
                       font=dict(size=11, color="#13343b"))

# Processing Layer boxes
processing_labels = ['PDF files', 'TXT files', 'MD files', 'PyMuPDF', 'Text reader', 'Text reader']
processing_colors = ['#FFCDD2', '#FFCDD2', '#FFCDD2', '#9FA8B0', '#9FA8B0', '#9FA8B0']

for i, (x, y, label, color) in enumerate(zip(processing_x, processing_y_vals, processing_labels, processing_colors)):
    fig.add_shape(type="rect", x0=x-0.35, y0=y-0.12, x1=x+0.35, y1=y+0.12,
                  line=dict(color="#21808d", width=2), fillcolor=color)
    fig.add_annotation(x=x, y=y, text=label, showarrow=False,
                       font=dict(size=10, color="#13343b"))

# Output Layer boxes
output_labels = ['Task DB', 'JSON Results', 'Logging']
output_colors = ['#FFEB8A', '#FFEB8A', '#FFEB8A']

for i, (x, label) in enumerate(zip(output_x, output_labels)):
    fig.add_shape(type="rect", x0=x-0.4, y0=output_y-0.15, x1=x+0.4, y1=output_y+0.15,
                  line=dict(color="#D2BA4C", width=2), fillcolor=output_colors[i])
    fig.add_annotation(x=x, y=output_y, text=label, showarrow=False,
                       font=dict(size=11, color="#13343b"))

# Add arrows/connections
# Client to Core
arrows = [
    # Client to Core
    (1, client_y-0.15, 1, core_y+0.15),  # Python -> zai_reader
    (2.5, client_y-0.15, 2.5, core_y+0.15),  # REST -> app.py (should go to 4)
    (4, client_y-0.15, 4, core_y+0.15),  # CLI -> zai_reader (should go to 1)
    # Core connections
    (1, core_y-0.15, 2.5, core_y+0.15),  # zai_reader -> DocumentReader
    (4, core_y-0.15, 2.5, core_y+0.15),  # app.py -> DocumentReader
    # Core to Processing (DocumentReader to files)
    (2.5, core_y-0.15, 0.5, 1.82),  # to PDF
    (2.5, core_y-0.15, 2, 1.82),  # to TXT
    (2.5, core_y-0.15, 3.5, 1.82),  # to MD
    # Files to extractors
    (0.5, 1.58, 0.5, 1.42),  # PDF to PyMuPDF
    (2, 1.58, 2, 1.42),  # TXT to Text reader
    (3.5, 1.58, 3.5, 1.42),  # MD to Text reader
    # Extractors to Output
    (0.5, 1.18, 1, output_y+0.15),  # PyMuPDF to Task DB
    (2, 1.18, 1, output_y+0.15),  # Text reader to Task DB
    (3.5, 1.18, 1, output_y+0.15),  # Text reader to Task DB
    # Task DB to JSON
    (1, output_y-0.15, 2.5, output_y+0.15),  # Task DB to JSON
    # DocumentReader to Logging
    (2.5, core_y-0.15, 4, output_y+0.15),  # DocumentReader to Logging
    # JSON back to clients
    (2.5, output_y+0.15, 1, client_y-0.15),  # JSON to Python
    (2.5, output_y+0.15, 2.5, client_y-0.15),  # JSON to REST
]

# Corrected arrows
arrows = [
    # Client to Core
    (1, client_y-0.15, 1, core_y+0.15),  # Python -> zai_reader
    (2.5, client_y-0.15, 4, core_y+0.15),  # REST -> app.py
    (4, client_y-0.15, 1, core_y+0.15),  # CLI -> zai_reader
    # Core internal
    (1.4, core_y, 2.1, core_y),  # zai_reader -> DocumentReader
    (3.6, core_y, 2.9, core_y),  # app.py -> DocumentReader
    # Core to Processing
    (2.3, core_y-0.15, 0.5, 1.82),  # to PDF
    (2.5, core_y-0.15, 2, 1.82),  # to TXT
    (2.7, core_y-0.15, 3.5, 1.82),  # to MD
    # Files to extractors
    (0.5, 1.58, 0.5, 1.42),
    (2, 1.58, 2, 1.42),
    (3.5, 1.58, 3.5, 1.42),
    # Extractors to DB
    (0.7, 1.18, 1, output_y+0.15),
    (2, 1.18, 1.2, output_y+0.15),
    (3.3, 1.18, 1.4, output_y+0.15),
    # DB to JSON
    (1.4, output_y, 2.1, output_y),
    # DocumentReader to Logging
    (2.7, core_y-0.15, 4, output_y+0.15),
    # JSON to clients
    (2.5, output_y+0.15, 1.2, client_y-0.15),
    (2.5, output_y+0.15, 2.5, client_y-0.15),
]

for x0, y0, x1, y1 in arrows:
    fig.add_annotation(
        x=x1, y=y1, ax=x0, ay=y0,
        xref='x', yref='y', axref='x', ayref='y',
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=1.5,
        arrowcolor='#21808d'
    )

# Add layer labels
fig.add_annotation(x=5.2, y=client_y, text="Client Layer", showarrow=False,
                   font=dict(size=12, color="#13343b", family="Arial Black"))
fig.add_annotation(x=5.2, y=core_y, text="Core Layer", showarrow=False,
                   font=dict(size=12, color="#13343b", family="Arial Black"))
fig.add_annotation(x=5.2, y=1.5, text="Processing", showarrow=False,
                   font=dict(size=12, color="#13343b", family="Arial Black"))
fig.add_annotation(x=5.2, y=output_y, text="Output", showarrow=False,
                   font=dict(size=12, color="#13343b", family="Arial Black"))

# Update layout
fig.update_layout(
    title="ZAI Reader System Architecture",
    xaxis=dict(range=[-0.5, 6], showgrid=False, showticklabels=False, zeroline=False),
    yaxis=dict(range=[0, 4], showgrid=False, showticklabels=False, zeroline=False),
    plot_bgcolor='#F3F3EE',
    paper_bgcolor='#F3F3EE',
    showlegend=False
)

# Save the figure
fig.write_image('architecture.png')
fig.write_image('architecture.svg', format='svg')
