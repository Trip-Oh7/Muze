import json
import os
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFloatingActionButton
from kivymd.uix.gridlayout import MDGridLayout
from kivy.uix.scrollview import ScrollView
from kivymd.uix.dialog import MDDialog
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.textinput import TextInput
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDIconButton
from kivymd.uix.label import MDLabel
from kivy.clock import Clock
from kivy.core.window import Window
import random




class NotesApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notes = []  # Store notes as a list of dictionaries
        self.categories = []  # List to store categories
        self.category_colors = {}  # Dictionary to store colors for categories
        self.current_note = None  # Keep track of the current note being edited
        self.notes_file = "notes.json"  # File path for the notes JSON

    def build(self):
        self.theme_cls.theme_style = "Dark"  # Set the theme to Dark
        screen = MDScreen()
        self.show_favorites = False  # Default state (not showing favorites)

        #my notes label
        label = MDLabel(text="My Notes", halign="center", pos_hint={"center_x":0.5, "center_y":0.95},
        theme_text_color="Primary", font_style="H5"
        )
        screen.add_widget(label)

        # Search bar
        self.search_bar = MDTextField(
            hint_text="Search notes...",
            pos_hint={"center_x": 0.5, "center_y": 0.9},
            size_hint_x=0.9,
        )
        self.search_bar.bind(text=self.on_search_text)  # Bind to text input to search as you type
        screen.add_widget(self.search_bar)

        # Scroll view for notes list
        self.scroll_view = ScrollView(
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            size_hint=(0.9, 0.7),
        )
        screen.add_widget(self.scroll_view)

        # Grid layout for notes
        self.notes_grid = MDGridLayout(
            cols=2,
            adaptive_height=True,
            padding="10dp",
            spacing="10dp",
        )
        self.scroll_view.add_widget(self.notes_grid)

        # Add note button
        self.add_note_button = MDFloatingActionButton(
            icon="plus",
            pos_hint={"center_x": 0.9, "center_y": 0.1},
            on_release=self.add_note,
        )
        screen.add_widget(self.add_note_button)

        # Toggle favorites button
        self.show_favorites_button = MDIconButton(
            icon="star-outline",  # Start with unfilled star
            pos_hint={"center_x": 0.95, "center_y": 0.95},
            on_release=self.toggle_favorites_view,
        )
        screen.add_widget(self.show_favorites_button)
        return screen  # Return the screen

    def on_start(self):
        """This method is called after the app starts and the UI is built."""
        self.load_notes_from_json()  # Load notes from JSON
        self.load_notes()  # Ensure notes are displayed after loading

    def random_color(self):
        return (random.random(), random.random(), random.random(), 1)  # RGBA color


    def load_notes_from_json(self):
        try:
            with open(self.notes_file, "r") as f:
                data_loaded = json.load(f) 

                # Load notes with color conversion
                self.notes = []
                for note_data in data_loaded.get("notes", []):  # Handle missing "notes" key
                    if "color" in note_data:
                        note_data["color"] = tuple(note_data["color"])
                    self.notes.append(note_data)

                # Load category colors
                self.category_colors = data_loaded.get("category_colors", {})  # Handle missing "category_colors" key

        except FileNotFoundError:
            self.notes = []
            self.category_colors = {}  # Initialize if no file
            with open(self.notes_file, 'w') as f:
                json.dump({"notes": self.notes, "category_colors": self.category_colors}, f, indent=4)
                
                
    def load_notes(self):
        self.notes_grid.clear_widgets()  # Clear current widgets
        for note in self.notes:
            self.add_note_to_grid(note)

    def add_note_to_grid(self, note):
        # Create a card for each note
        card = MDCard(
            size_hint_y=None,
            height="120dp",  # Increase height to accommodate two lines
            md_bg_color=note.get("color", (0.5, 0.7, 0.8, 1)),  # Use the note's color or default
            orientation="vertical",
            padding="10dp",
            on_release=lambda x: self.edit_note(note)  # Bind click to open note for editing
        )

        # Create a BoxLayout for the text area
        text_layout = MDBoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height="80dp",  # Set a height for the text layout
            spacing="5dp",  # Space between title and preview
        )

        # Add title as a label
        title_label = MDLabel(
            text=note["title"],
            theme_text_color="Primary",
            bold=True,
            size_hint_y=None,
            height="40dp",
            halign="left",  # Align text to the left
            valign="middle",  # Center vertically in its space
            font_style="H6",  # Use a larger font style (H6 is larger than the default)
        )
        title_label.bind(size=title_label.setter('text_size'))  # Ensure text wraps if needed
        text_layout.add_widget(title_label)

        # Add preview of the note as a label with fallback for missing "preview"
        preview_text = note.get("notes", "No content available")[:50] + "..."  # Get the first 50 characters or fallback message
        preview_label = MDLabel(
            text=preview_text,  # Use your note's preview text
            theme_text_color="Secondary",
            size_hint_y=None,
            height="40dp",  # Adjust height based on your preference
            halign="left",  # Align text to the left
            valign="middle",  # Center vertically in its space
            font_style="Body1",
            max_lines=3,
            shorten=True,
        )
        preview_label.bind(size=preview_label.setter('text_size'))  # Ensure text wraps if needed
        text_layout.add_widget(preview_label)

        # Create a horizontal BoxLayout for the text and star icon
        card_layout = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height="40dp",
            spacing="5dp",
            padding=[0, 10, 0, 0]  # Adjust padding as necessary
        )
        
        card_layout.add_widget(text_layout)  # Add the text layout to the card layout

        # Add a star icon if the note is favorited
        if note.get("favorite", False):
            star_icon = MDIconButton(
                icon="star",
                pos_hint={"center_y": 0.5},  # Center the star icon vertically
                size_hint=(None, None),
                size=("24dp", "24dp")  # Adjust size of the star icon
            )
            card_layout.add_widget(star_icon)  # Add star icon to the card layout

        # Add the card layout to the card
        card.add_widget(card_layout)

        self.notes_grid.add_widget(card)  # Add the card to the grid

    def save_notes_to_json(self):
        """Save notes and category colors to a JSON file."""
        data_to_save = {
            "notes": self.notes,
            "category_colors": self.category_colors  # Include category colors
        }
        with open(self.notes_file, 'w') as f:
            json.dump(data_to_save, f, indent=4)   
            
    def add_note(self, instance):
        self.current_note = None  # Reset current note for new note creation
        self.open_note_dialog()  # Open a new note dialog

    def open_note_dialog(self):
        # Initialize temp_note for a new note
        if not self.current_note:
            self.temp_note = {"favorite": False}  # Initialize a temporary note

        # Create the content for the dialog
        content = MDBoxLayout(orientation="vertical", spacing="5dp", padding="0dp")  # Remove padding
        content.size_hint_y = None  # Disable automatic height
        content.height = "480dp"  # Fixed height

        # Title bar with favorite button
        title_box = MDBoxLayout(
            orientation="horizontal", 
            size_hint_y=None, 
            height="40dp",  # Set minimal height
        )
        
        # Dialog title
        title_label = MDLabel(
            text="Edit Note" if self.current_note else "New Note", 
            bold=True,
            size_hint_x=0.9,  # Push the star icon to the right
            halign="left",  # Align to the left
            valign="middle"  # Vertically center the text
        )
        title_label.bind(size=title_label.setter('text_size'))  # Make sure text wraps if needed
        title_box.add_widget(title_label)

        # Star button for favorites aligned to the right
        self.favorite_button = MDIconButton(
            icon="star-outline",  # Default to unfilled star
            on_release=self.toggle_favorite if self.current_note else self.no_op,  # Use no-op if it's a new note
            pos_hint={"center_y": 0.5},  # Vertically center the star with the title
        )
        
        # Optionally disable the star button for new notes
        if not self.current_note:  # If it's a new note
            self.favorite_button.disabled = True  # Disable the button

        title_box.add_widget(self.favorite_button)

        # Add the title box to the content
        content.add_widget(title_box)

        # Title text field directly under the title bar
        self.title_field = MDTextField(
            hint_text="Title", 
            size_hint_y=None, 
            height="40dp",  # Height for title field
        )
        content.add_widget(self.title_field)

        # Add a category text field
        self.category_field = MDTextField(
            hint_text="Category",
            size_hint_y=None,
            height="40dp",
        )
        self.category_field.bind(on_text=self.on_category_text)  # Bind the event to filter categories
        content.add_widget(self.category_field)

        # URL text field and Go button
        url_box = MDBoxLayout(spacing="10dp", size_hint_y=None, height="40dp")
        self.url_field = MDTextField(hint_text="URL")
        url_box.add_widget(self.url_field)
        go_button = MDRaisedButton(text="Go", on_release=self.open_url)
        url_box.add_widget(go_button)
        content.add_widget(url_box)

        # Notes text input, taller size
        self.notes_field = TextInput(
            hint_text="Notes", 
            multiline=True, 
            size_hint_y=0.8,  # Height for the notes field
            padding=[10, 10],  
            input_type='text',  # Set input type to "text" for standard keyboard behavior
            keyboard_suggestions=True,  # Enable suggestions from the keyboard
            use_bubble=True,  # Enable the selection and copy-paste bubble
            use_handles=True,  # Enable selection handles for easy text selection
        )
        content.add_widget(self.notes_field)

        # Buttons box for Save, Delete, and Cancel
        buttons_box = MDBoxLayout(spacing="10dp", size_hint_y=None, height="40dp")

        # Cancel button
        cancel_button = MDRaisedButton(text="Cancel", on_release=self.close_dialog)
        buttons_box.add_widget(cancel_button)

        # Delete button if editing an existing note
        if self.current_note:
            delete_button = MDRaisedButton(text="Delete", on_release=self.delete_note)
            buttons_box.add_widget(delete_button)

        # Save button
        save_button = MDRaisedButton(text="Save", on_release=self.save_note)
        buttons_box.add_widget(save_button)

        # Add the buttons box to the content
        content.add_widget(buttons_box)

        # Create the dialog
        self.dialog = MDDialog(
            type="custom",
            content_cls=content,
            size_hint=(0.9, None),  # Use auto height for the dialog
            pos_hint={'center_x': 0.5, 'center_y': 0.7},
            height="480dp",  # Fixed height for the dialog
        )

        # Populate fields if editing an existing note
        if self.current_note:
            self.title_field.text = self.current_note["title"]
            self.url_field.text = self.current_note["url"]
            self.notes_field.text = self.current_note["notes"]
            self.category_field.text = self.current_note.get("category", "")  

        # Update the star icon based on whether it's a favorite
        if self.current_note and self.current_note.get("favorite", False):
            self.favorite_button.icon = "star"  # Filled star
        else:
            self.favorite_button.icon = "star-outline"  # Unfilled star

        self.dialog.open()

    def no_op(self):
        pass


    def toggle_favorite(self, *args):
        """Toggle favorite status when the star button is clicked."""
        if self.current_note is None:
            # Initialize a new note if it doesn't exist yet
            self.current_note = {
                "title": self.title_field.text.strip(),
                "url": self.url_field.text.strip(),
                "notes": self.notes_field.text.strip(),
                "category": self.category_field.text.strip().lower(),  # Include category and format properly
                "color": self.category_colors.get(self.category_field.text.strip().lower(), self.random_color()),  # Assign color
                "favorite": False  # Default to not favorited
            }
            # Append the new note to the notes list
            self.notes.append(self.current_note)
        
        # Toggle the favorite status
        self.current_note["favorite"] = not self.current_note.get("favorite", False)
        
        # Update the star icon based on the new favorite status
        self.favorite_button.icon = "star" if self.current_note["favorite"] else "star-outline"
        
        # Save the notes to JSON immediately to persist the favorite status
        self.save_notes_to_json()
        self.update_notes_grid(self.current_note)  # Add this function call to refresh the UI


    def close_dialog(self, *args):
        if self.dialog:
            self.dialog.dismiss()

    def open_url(self, instance):
        import webbrowser
        url = self.url_field.text
        if url:
            webbrowser.open(url)

    def save_note(self, instance):
        title = self.title_field.text.strip()  # Get the title from the input field
        url = self.url_field.text.strip()  # Get the URL from the input field
        notes = self.notes_field.text.strip()  # Get the notes from the input field
        category = self.category_field.text.strip().lower()  # Get the category from the input field

        # Check if the category already has an assigned color
        if category in self.category_colors:
            color = self.category_colors[category]
        else:
            color = self.random_color()  # Assign a new random color
            self.category_colors[category] = color  # Store the color for the category

        # If editing an existing note, update it instead of creating a new one
        if self.current_note:
            self.current_note["title"] = title
            self.current_note["url"] = url
            self.current_note["notes"] = notes
            self.current_note["category"] = category
            self.current_note["color"] = color  # Update color
        else:
            # Create a new note with the assigned color
            self.current_note = {
                "title": title,
                "url": url,  # Include the URL if needed
                "notes": notes,
                "category": category,
                "color": color,  # Assign the color from the dictionary
                "favorite": False  # Default value for favorite
            }
            # Add the category to the list of categories if it doesn't already exist
            if category not in self.categories:
                self.categories.append(category)

            # Add the note to the notes list
            self.notes.append(self.current_note)  # Make sure this line is included

        self.save_notes_to_json()  # Save notes to JSON
        self.load_notes()  # Reload notes to update the display
        self.close_dialog()  # Close the dialog after saving

    def on_category_text(self, instance, value):
        """Auto-fill categories based on the input text."""
        # Convert input to lowercase for case-insensitive matching
        filtered_categories = [cat for cat in self.categories if value.lower() in cat.lower()]
        
        # Here you can implement a dropdown or display filtered suggestions
        # For example, using MDDropdownMenu to show suggestions
        print(filtered_categories)  # You can replace this with actual dropdown logic

    def delete_note(self, instance):
        if self.current_note in self.notes:
            self.notes.remove(self.current_note)
        self.save_notes_to_json()  # Save notes to JSON after deleting
        self.load_notes()  # Reload notes after deleting
        self.close_dialog()

    def on_search_text(self, instance, value):
        """Filter notes based on the search query, including title, category, and notes."""
        filtered_notes = [
            note for note in self.notes 
            if (
                value.lower() in note["title"].lower() or 
                value.lower() in note.get("category", "").lower() or 
                value.lower() in note.get("notes", "").lower()  # Check if value is in notes
            )
        ]
        
        self.notes_grid.clear_widgets()
        for note in filtered_notes:
            self.add_note_to_grid(note)
            
    def edit_note(self, note):
        """Edit an existing note by opening the dialog with the note details pre-filled."""
        self.current_note = note  # Set the current note to the one clicked
        self.open_note_dialog()  # Open the note dialog with the note's data pre-filled


    def toggle_favorites_view(self, *args):
        """Toggle between showing all notes and only favorite notes."""
        self.show_favorites = not self.show_favorites  # Flip the state

        # Update the icon and text based on the state
        if self.show_favorites:
            self.show_favorites_button.icon = "star"  # Filled star when favorites are shown
            self.show_favorites_button.text = "Show All"  # Change button text
            self.show_favorite_notes()  # Show only favorite notes
        else:
            self.show_favorites_button.icon = "star-outline"  # Unfilled star when favorites are hidden
            self.show_favorites_button.text = "Show Favorites"  # Reset button text
            self.load_notes()  # Load all notes

        # Fade out and then back in
        self.notes_grid.opacity = 0  # Hide the grid
        Clock.schedule_once(self.update_notes_grid, 0.1)  # Wait a moment before updating

    def update_notes_grid(self, dt):
        """Update the notes grid and then make it visible again."""
        self.notes_grid.clear_widgets()  # Clear current widgets
        if self.show_favorites:
            favorite_notes = [note for note in self.notes if note.get("favorite", False)]
            for note in favorite_notes:
                self.add_note_to_grid(note)
        else:
            for note in self.notes:
                self.add_note_to_grid(note)

        self.notes_grid.opacity = 1  # Show the grid again



    def show_favorite_notes(self):
        """Filter and display only favorite notes."""
        self.notes_grid.clear_widgets()  # Clear current widgets
        favorite_notes = [note for note in self.notes if note.get("favorite", False)]  # Filter only favorite notes
        
        for note in favorite_notes:
            self.add_note_to_grid(note)

if __name__ == "__main__":
    NotesApp().run()
