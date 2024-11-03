from IPython.core.magic import register_line_magic, Magics, magics_class
from IPython.display import display, Markdown, HTML, Javascript
from IPython import get_ipython
from datawizzy.nlp_processor import NLPProcessor
from datawizzy.instruction_generator import InstructionGenerator
from datawizzy.safety import SafetyChecker
import uuid
import html

@magics_class
class DataWizardMagics(Magics):
    def __init__(self, shell):
        super(DataWizardMagics, self).__init__(shell)
        self.nlp = NLPProcessor()
        self.safety = SafetyChecker()
        self.generator = InstructionGenerator()
        self.conversation_history = ""
        self.comm_manager = shell.kernel.comm_manager
        self.comm_manager.register_target('need_more_info_comm', self.comm_target_handler)

    def comm_target_handler(self, comm, open_msg):
        """
        Handler for Comm messages from the frontend.
        """
        @comm.on_msg
        def _recv(msg):
            data = msg['content']['data']
            query = data.get('query', '')
            conversation_history = data.get('conversation_history', '')
            # Generate detailed instructions
            try:
                detailed_instructions = self.nlp.generate_detailed_instructions(query, conversation_history)
            except Exception as e:
                response = f"Error generating detailed instructions: {e}"
                comm.send({'status': 'error', 'message': response})
                return

            # Safety check
            if self.safety.check_content(detailed_instructions):
                instructions = self.generator.format_instructions(detailed_instructions)
                comm.send({'status': 'success', 'detailed_instructions': instructions})
            else:
                response = "The detailed content was deemed unsafe."
                comm.send({'status': 'unsafe', 'message': response})

    @register_line_magic
    def datawizard(self, line):
        """
        Magic command to handle data science queries.
        Usage: %datawizard your query here
        """
        query = line.strip()
        if not query:
            display(Markdown("**DataWizzy AI:**\n\nPlease provide a valid query."))
            return

        # Update conversation history
        self.conversation_history += f"User: {query}\n"

        # Generate initial instructions
        try:
            raw_instructions = self.nlp.generate_instructions(query, self.conversation_history)
        except Exception as e:
            display(Markdown(f"**DataWizzy AI:**\n\nError generating instructions: {e}"))
            return

        # Safety check for initial instructions
        if self.safety.check_content(raw_instructions):
            instructions = self.generator.format_instructions(raw_instructions)
            display(Markdown(f"**DataWizzy AI:**\n\n{instructions}"))
            self.conversation_history += f"DataWizzy AI: {instructions}\n"
        else:
            display(Markdown("**DataWizzy AI:**\n\nThe generated content was deemed unsafe."))
            return

        # Generate a unique identifier for this interaction
        interaction_id = str(uuid.uuid4())

        # HTML and JavaScript for the "Need More Info" button
        button_html = f"""
        <button id="need_more_info_{interaction_id}" style="margin-top: 10px;">Need More Info</button>
        <div id="detailed_info_{interaction_id}" style="margin-top: 10px;"></div>

        <script>
            (function() {{
                var button = document.getElementById("need_more_info_{interaction_id}");
                var output = document.getElementById("detailed_info_{interaction_id}");

                // Establish a Comm channel
                var comm = Jupyter.notebook.kernel.comm_manager.new_comm('need_more_info_comm', {{}});
                
                button.onclick = function() {{
                    button.disabled = true;
                    button.innerText = "Fetching more information...";
                    // Send the query and conversation history to the backend
                    comm.send({{
                        'query': `{html.escape(query)}`,
                        'conversation_history': `{html.escape(self.conversation_history)}`
                    }});
                }};

                // Handle responses from the backend
                comm.on_msg(function(msg) {{
                    var data = msg.content.data;
                    if (data.status === 'success') {{
                        output.innerHTML = `<div style="border:1px solid #ccc; padding:10px; border-radius:5px; background-color:#f9f9f9;"><strong>DataWizzy AI (Detailed):</strong><br><br>${{data.detailed_instructions.replace(/\\n/g, '<br>')}}</div>`;
                    }} else if (data.status === 'unsafe') {{
                        output.innerHTML = `<div style="color:red;"><strong>DataWizzy AI:</strong> ${data.message}</div>`;
                    }} else {{
                        output.innerHTML = `<div style="color:red;"><strong>Error:</strong> ${data.message}</div>`;
                    }}
                }});
            }})();
        </script>
        """

        display(HTML(button_html))

def load_ipython_extension(ipython):
    ipython.register_magics(DataWizardMagics)

# To enable the extension, users should load it in their Jupyter notebook:
# %load_ext jupyter_extension
