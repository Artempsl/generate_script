"""
Quick test to check if project_slug persists through the graph.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from agent.graph import create_agent_graph
from agent.models import create_initial_state, ScriptRequestItem

# Create minimal test request
request = ScriptRequestItem(
    request_id="test-slug-debug",
    project_name="Slug Debug Test",
    genre="comedy",
    story_idea="A quick test to check state persistence",
    duration=1
)

# Create initial state
initial_state = create_initial_state(request)
print(f"\n1. Initial state project_slug: '{initial_state.get('project_slug')}'")
print(f"   Initial state project_dir: '{initial_state.get('project_dir')}'")

# Create and invoke graph
graph = create_agent_graph()
print(f"\n2. Running graph...")

try:
    final_state = graph.invoke(initial_state)
    
    print(f"\n3. Final state project_slug: '{final_state.get('project_slug')}'")
    print(f"   Final state project_dir: '{final_state.get('project_dir')}'")
    print(f"   Script generated: {len(final_state.get('script', ''))} chars")
    print(f"   Segments created: {final_state.get('segment_count', 0)}")
    print(f"   Audio files: {final_state.get('audio_files_count', 0)}")
    
    # Check what was actually saved
    from pathlib import Path
    project_folder = Path("projects") / final_state.get('project_slug', 'UNKNOWN')
    if project_folder.exists():
        files = list(project_folder.iterdir())
        print(f"\n4. Files in {project_folder}:")
        for f in files:
            print(f"   - {f.name} ({f.stat().st_size} bytes)")
    else:
        print(f"\n4. Project folder NOT found: {project_folder}")
        
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
