import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.widgets import Button, RadioButtons, TextBox
import yaml
import numpy as np

class FloorPlanEditor:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(14, 10))
        plt.subplots_adjust(left=0.25, bottom=0.15)
        
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_title('Fire Evacuation Floor Plan Editor', fontsize=14, fontweight='bold')
        
        # Data structures
        self.junctions = []
        self.terminals = []
        self.rooms = []
        self.corridors = []
        self.room_connections = []
        self.fire_exits = []
        
        # Drawing state
        self.mode = 'junction'
        self.room_start = None
        self.corridor_start = None
        self.room_connection_start = None
        self.fire_exit_start = None
        self.node_id_counter = {'J': 1, 'T': 1, 'R': 1, 'FE': 1, 'C': 1}
        
        # Visual elements
        self.node_artists = []
        self.room_artists = []
        self.corridor_artists = []
        
        # Setup UI
        self.setup_ui()
        self.setup_event_handlers()
        
    def setup_ui(self):
        # Mode selector
        ax_radio = plt.axes([0.02, 0.5, 0.15, 0.3])
        self.radio = RadioButtons(ax_radio, 
                                  ('Junction', 'Terminal', 'Room', 'Fire Exit', 'Corridor', 'Connect Room', 'Room Link'),
                                  active=0)
        self.radio.on_clicked(self.set_mode)
        
        # Buttons
        ax_save = plt.axes([0.02, 0.40, 0.15, 0.04])
        self.btn_save = Button(ax_save, 'Save to YAML')
        self.btn_save.on_clicked(self.save_yaml)
        
        ax_clear = plt.axes([0.02, 0.35, 0.15, 0.04])
        self.btn_clear = Button(ax_clear, 'Clear All')
        self.btn_clear.on_clicked(self.clear_all)
        
        ax_undo = plt.axes([0.02, 0.30, 0.15, 0.04])
        self.btn_undo = Button(ax_undo, 'Undo Last')
        self.btn_undo.on_clicked(self.undo_last)
        
        # Instructions
        instructions = (
            "INSTRUCTIONS:\n\n"
            "Junction: Click to place\n"
            "Terminal: Click to place\n"
            "Room: Click-drag to draw\n"
            "Fire Exit: Click node\n"
            "Corridor: Click two nodes\n"
            "Connect Room: Click room\n"
            "  then junction\n\n"
            "Right-click to cancel"
        )
        self.ax.text(0.02, 0.95, instructions, transform=self.fig.transFigure,
                    fontsize=9, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
    def setup_event_handlers(self):
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('button_release_event', self.on_release)
        
    def set_mode(self, label):
        mode_map = {
            'Junction': 'junction',
            'Terminal': 'terminal',
            'Room': 'room',
            'Fire Exit': 'fire_exit',
            'Corridor': 'corridor',
            'Connect Room': 'connect_room',
            'Room Link': 'room_link'
        }
        self.mode = mode_map[label]
        self.corridor_start = None
        self.room_start = None
        self.room_connection_start = None
        self.fire_exit_start = None
        
    def on_click(self, event):
        if event.inaxes != self.ax or event.button == 3:  # Right click cancels
            self.room_start = None
            self.corridor_start = None
            self.room_connection_start = None
            self.fire_exit_start = None
            return
            
        x, y = round(event.xdata, 1), round(event.ydata, 1)
        
        if self.mode == 'junction':
            self.add_junction(x, y)
        elif self.mode == 'terminal':
            self.add_terminal(x, y)
        elif self.mode == 'room':
            self.room_start = (x, y)
        elif self.mode == 'fire_exit':
            self.handle_fire_exit_click(x, y)
        elif self.mode == 'corridor':
            self.handle_corridor_click(x, y)
        elif self.mode == 'connect_room':
            self.handle_room_connection_click(x, y)
        elif self.mode == 'room_link':
            self.handle_room_link_click(x, y)
            
    def on_release(self, event):
        if self.mode == 'room' and self.room_start and event.inaxes == self.ax:
            x, y = round(event.xdata, 1), round(event.ydata, 1)
            self.add_room(self.room_start, (x, y))
            self.room_start = None
            
    def add_junction(self, x, y):
        node_id = f"J{self.node_id_counter['J']}"
        self.node_id_counter['J'] += 1
        
        self.junctions.append({
            'id': node_id,
            'position': [x, y]
        })
        
        artist = self.ax.plot(x, y, 'o', color='yellow', markersize=12, 
                             markeredgecolor='black', markeredgewidth=1.5)[0]
        self.ax.text(x, y, node_id, ha='center', va='center', fontsize=8, fontweight='bold')
        self.node_artists.append(artist)
        self.fig.canvas.draw()
        
    def add_terminal(self, x, y):
        node_id = f"T{self.node_id_counter['T']}"
        self.node_id_counter['T'] += 1
        
        self.terminals.append({
            'id': node_id,
            'position': [x, y]
        })
        
        artist = self.ax.plot(x, y, 'o', color='red', markersize=12,
                             markeredgecolor='black', markeredgewidth=1.5)[0]
        self.ax.text(x, y, node_id, ha='center', va='center', fontsize=8, fontweight='bold')
        self.node_artists.append(artist)
        self.fig.canvas.draw()
        
    def add_room(self, start, end):
        x1, y1 = start
        x2, y2 = end
        
        # Calculate center and dimensions
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        
        if width < 2 or height < 2:
            return
            
        node_id = f"R{self.node_id_counter['R']}"
        self.node_id_counter['R'] += 1
        
        self.rooms.append({
            'id': node_id,
            'attached_to': None,
            'door_cost': 2.0,
            'bounds': {
                'x': min(x1, x2),
                'y': min(y1, y2),
                'width': width,
                'height': height
            },
            'center': (center_x, center_y)
        })
        
        # Draw room rectangle
        rect = patches.Rectangle((min(x1, x2), min(y1, y2)), width, height,
                                 linewidth=2, edgecolor='blue', facecolor='lightblue', alpha=0.3)
        self.ax.add_patch(rect)
        self.room_artists.append(rect)
        
        # Draw room center point
        artist = self.ax.plot(center_x, center_y, 'o', color='blue', markersize=10,
                             markeredgecolor='black', markeredgewidth=1.5)[0]
        self.ax.text(center_x, center_y, node_id, ha='center', va='center', 
                    fontsize=8, fontweight='bold', color='white')
        self.node_artists.append(artist)
        
        self.fig.canvas.draw()
        print(f"Added room {node_id}. Now use 'Connect Room' mode to attach it to a junction.")
        
    def handle_corridor_click(self, x, y):
        if self.corridor_start is None:
            # Find nearest node
            all_nodes = self.junctions + self.terminals
            node = self.find_nearest_node(x, y, all_nodes, threshold=5)
            
            if node:
                self.corridor_start = node
                print(f"Corridor start: {node['id']}. Click another node to complete.")
            else:
                print("Click near a junction or terminal!")
        else:
            # Find end node
            all_nodes = self.junctions + self.terminals
            node = self.find_nearest_node(x, y, all_nodes, threshold=5)
            
            if node and node['id'] != self.corridor_start['id']:
                self.add_corridor(self.corridor_start, node)
                self.corridor_start = None
            else:
                print("Click a different node!")
                
    def add_corridor(self, node1, node2):
        x1, y1 = node1['position']
        x2, y2 = node2['position']
        length = round(np.sqrt((x2 - x1)**2 + (y2 - y1)**2), 1)

        corridor_id = f"C{self.node_id_counter['C']}"
        self.node_id_counter['C'] += 1
        
        self.corridors.append({
            'id': corridor_id,
            'from': node1['id'],
            'to': node2['id'],
            'length': length
        })
        
        line = self.ax.plot([x1, x2], [y1, y2], 'k-', linewidth=3)[0]
        line.set_zorder(-1)  # Send corridor behind nodes
        self.corridor_artists.append(line)
        
        # Draw length label
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        self.ax.text(mid_x, mid_y, f'{length}', fontsize=8, 
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.7))
        
        self.fig.canvas.draw()
        print(f"Added corridor: {node1['id']} -> {node2['id']} (length: {length})")
        
    def find_nearest_node(self, x, y, nodes, threshold=100):
        if not nodes:
            return None
            
        min_dist = float('inf')
        nearest = None
        
        for node in nodes:
            nx, ny = node['position']
            dist = np.sqrt((x - nx)**2 + (y - ny)**2)
            if dist < min_dist:
                min_dist = dist
                nearest = node
                
        return nearest if min_dist < threshold else None
        
    def handle_room_connection_click(self, x, y):
        if self.room_connection_start is None:
            # First click: select a room
            room = self.find_nearest_room(x, y, threshold=10)
            if room:
                self.room_connection_start = room
                print(f"Selected room {room['id']}. Now click a junction to attach it.")
            else:
                print("Click near a room!")
        else:
            # Second click: select a junction
            junction = self.find_nearest_node(x, y, self.junctions, threshold=10)
            if junction:
                self.connect_room_to_junction(self.room_connection_start, junction)
                self.room_connection_start = None
            else:
                print("Click near a junction!")
                
    def find_nearest_room(self, x, y, threshold=100):
        if not self.rooms:
            return None
            
        min_dist = float('inf')
        nearest = None
        
        for room in self.rooms:
            center_x, center_y = room['center']
            dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
            if dist < min_dist:
                min_dist = dist
                nearest = room
                
        return nearest if min_dist < threshold else None
        
    def connect_room_to_junction(self, room, junction):
        room['attached_to'] = junction['id']
        
        center_x, center_y = room['center']
        junction_x, junction_y = junction['position']
        
        # Draw portal connection (dashed orange line)
        line = self.ax.plot([center_x, junction_x], 
                           [center_y, junction_y], 
                           'orange', linewidth=2, linestyle='--', alpha=0.6)[0]
        self.corridor_artists.append(line)
        
        # Draw portal point
        portal_x = (center_x + junction_x) / 2
        portal_y = (center_y + junction_y) / 2
        portal_artist = self.ax.plot(portal_x, portal_y, 'o', color='orange', 
                                    markersize=8, markeredgecolor='black', markeredgewidth=1)[0]
        self.node_artists.append(portal_artist)
        
        self.fig.canvas.draw()
        print(f"Connected {room['id']} to {junction['id']}")
        
    def handle_fire_exit_click(self, x, y):
        # Find nearest node (junction, terminal, or room)
        all_nodes = self.junctions + self.terminals
        all_rooms = [(r['center'][0], r['center'][1], r) for r in self.rooms]
        
        junction = self.find_nearest_node(x, y, all_nodes, threshold=10)
        
        nearest_room = None
        if self.rooms:
            min_dist = float('inf')
            for cx, cy, room in all_rooms:
                dist = np.sqrt((x - cx)**2 + (y - cy)**2)
                if dist < min_dist and dist < 10:
                    min_dist = dist
                    nearest_room = room
        
        if junction:
            self.add_fire_exit(junction['id'], junction['position'])
        elif nearest_room:
            self.add_fire_exit(nearest_room['id'], nearest_room['center'])
        else:
            print("Click near a node (junction, terminal, or room)!")
            
    def add_fire_exit(self, node_id, position):
        fe_id = f"FE{self.node_id_counter['FE']}"
        self.node_id_counter['FE'] += 1
        
        self.fire_exits.append({
            'id': fe_id,
            'attached_to': node_id
        })
        
        # Draw fire exit sign (red triangle marker)
        x, y = position
        offset = 3  # Offset from node center
        artist = self.ax.plot(x + offset, y + offset, '^', color='red', 
                             markersize=10, markeredgecolor='darkred', markeredgewidth=1.5)[0]
        self.node_artists.append(artist)
        
        # Add label
        self.ax.text(x + offset + 1, y + offset + 1, fe_id, fontsize=7, 
                    color='red', fontweight='bold')
        
        self.fig.canvas.draw()
        print(f"Added fire exit {fe_id} to {node_id}")
        
    def handle_room_link_click(self, x, y):
        if self.room_connection_start is None:
            # First click: select a room
            room = self.find_nearest_room(x, y, threshold=10)
            if room:
                self.room_connection_start = room
                print(f"Selected room {room['id']}. Now click another room to link it.")
            else:
                print("Click near a room!")
        else:
            # Second click: select another room
            room = self.find_nearest_room(x, y, threshold=10)
            if room and room['id'] != self.room_connection_start['id']:
                self.add_room_connection(self.room_connection_start, room)
                self.room_connection_start = None
            else:
                print("Click a different room!")
                
    def add_room_connection(self, room1, room2):
        x1, y1 = room1['center']
        x2, y2 = room2['center']
        cost = round(np.sqrt((x2 - x1)**2 + (y2 - y1)**2), 1)
        
        self.room_connections.append({
            'from': room1['id'],
            'to': room2['id'],
            'cost': cost
        })
        
        # Draw connection line (green dashed)
        line = self.ax.plot([x1, x2], [y1, y2], 'g--', linewidth=2, alpha=0.6)[0]
        self.corridor_artists.append(line)
        
        # Draw cost label
        mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
        self.ax.text(mid_x, mid_y, f'{cost}', fontsize=8,
                    bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.7))
        
        self.fig.canvas.draw()
        print(f"Linked {room1['id']} to {room2['id']} (cost: {cost})")
        
    def save_yaml(self, event):
        def to_float(value):
            return float(value) if isinstance(value, (np.floating,)) else value

        junctions_export = [
            {
                'id': j['id'],
                'position': [to_float(j['position'][0]), to_float(j['position'][1])]
            }
            for j in self.junctions
        ]

        terminals_export = [
            {
                'id': t['id'],
                'position': [to_float(t['position'][0]), to_float(t['position'][1])]
            }
            for t in self.terminals
        ]

        rooms_export = [
            {
                'id': r['id'],
                'attached_to': r['attached_to'],
                'door_cost': to_float(r.get('door_cost', 1.0))
            }
            for r in self.rooms
        ]

        corridors_export = [
            {
                'id': c.get('id'),
                'from': c['from'],
                'to': c['to'],
                'length': to_float(c['length'])
            }
            for c in self.corridors
        ]

        room_connections_export = [
            {
                'from': rc['from'],
                'to': rc['to'],
                'cost': to_float(rc['cost'])
            }
            for rc in self.room_connections
        ]

        data = {
            'units': 'meters',
            'junctions': junctions_export,
            'terminals': terminals_export,
            'corridors': corridors_export,
            'rooms': rooms_export,
            'room_connections': room_connections_export,
            'fire_exits': self.fire_exits
        }
        
        with open('dsl.yaml', 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
        print("\n" + "="*50)
        print("✓ Saved to dsl.yaml successfully!")
        print(f"  - {len(self.junctions)} junctions")
        print(f"  - {len(self.terminals)} terminals")
        print(f"  - {len(self.rooms)} rooms")
        print(f"  - {len(self.corridors)} corridors")
        print(f"  - {len(self.room_connections)} room connections")
        print(f"  - {len(self.fire_exits)} fire exits")
        print("="*50 + "\n")
        
    def undo_last(self, event):
        # Remove last added element
        if self.node_artists:
            artist = self.node_artists.pop()
            artist.remove()
            
        if self.corridors and len(self.corridor_artists) > 0:
            artist = self.corridor_artists.pop()
            artist.remove()
            self.corridors.pop()
        elif self.rooms and len(self.room_artists) > 0:
            artist = self.room_artists.pop()
            artist.remove()
            self.rooms.pop()
        elif self.fire_exits:
            self.fire_exits.pop()
        elif self.terminals:
            self.terminals.pop()
        elif self.junctions:
            self.junctions.pop()
            
        self.fig.canvas.draw()
        
    def clear_all(self, event):
        self.ax.clear()
        self.ax.set_xlim(0, 100)
        self.ax.set_ylim(0, 100)
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        self.ax.set_title('Fire Evacuation Floor Plan Editor', fontsize=14, fontweight='bold')
        
        self.junctions = []
        self.terminals = []
        self.rooms = []
        self.corridors = []
        self.room_connections = []
        self.fire_exits = []
        
        self.node_artists = []
        self.room_artists = []
        self.corridor_artists = []
        
        self.node_id_counter = {'J': 1, 'T': 1, 'R': 1, 'FE': 1, 'C': 1}
        
        self.fig.canvas.draw()
        print("Cleared all elements!")
        
    def show(self):
        plt.show()

if __name__ == '__main__':
    print("="*60)
    print("FIRE EVACUATION FLOOR PLAN EDITOR")
    print("="*60)
    print("\nStarting interactive editor...")
    print("\nColor Legend:")
    print("  🟡 Yellow = Junction nodes")
    print("  🔴 Red = Terminal (exit) nodes")
    print("  🔵 Blue = Room nodes")
    print("  � Orange = Portal connections")
    print("  ⬛ Black = Corridors")
    print("  🔺 Red Triangle = Fire Exit Signs")
    print("  🟢 Green Dash = Room Links\n")
    
    editor = FloorPlanEditor()
    editor.show()
