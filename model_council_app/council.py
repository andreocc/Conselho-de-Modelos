import asyncio
import ollama
import config

class ModelCouncil:
    @staticmethod
    def get_available_models():
        try:
            models_info = ollama.list()
            # Handle response whether it's a dict or object
            # New versions return an object with a 'models' attribute containing Model objects
            
            models_list = []
            if hasattr(models_info, 'models'):
                models_list = models_info.models
            elif isinstance(models_info, dict) and 'models' in models_info:
                models_list = models_info['models']
            else:
                # Fallback if it returns list directly
                models_list = models_info

            # Extract names
            names = []
            for m in models_list:
                if hasattr(m, 'model'):
                    names.append(m.model)
                elif isinstance(m, dict):
                    names.append(m.get('model') or m.get('name'))
            return names
        except Exception as e:
            print(f"Error fetching models: {e}")
            return []

    @staticmethod
    async def query_model(model_name, prompt, context=None, temperature=config.DEFAULT_TEMPERATURE, system_prompt=None):
        """
        Queries a single model asynchronously.
        """
        full_prompt = prompt
        
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
            
        if context:
            # We can put context in a system message or user message. 
            # Usually putting it in user or system depends on model, but appending to prompt is safest for generic use.
            full_prompt = f"Context information is below.\n---------------------\n{context}\n---------------------\nGiven the context information and not prior knowledge, answer the query.\nQuery: {prompt}"
        
        messages.append({'role': 'user', 'content': full_prompt})

        try:
            client = ollama.AsyncClient()
            response = await client.chat(
                model=model_name, 
                messages=messages,
                options={'temperature': temperature},
                stream=False # Keep False for basic implementation first, True for advanced streaming
            )
            return {
                "model": model_name,
                "response": response['message']['content'],
                "status": "Success"
            }
        except Exception as e:
            return {
                "model": model_name,
                "response": f"Error: {str(e)}",
                "status": "Error"
            }

    @staticmethod
    async def run_council(selected_models, prompt, context_chunks=None, persona_mode="Padrão (Neutro)"):
        """
        Runs the prompt against all selected models in parallel with Persona injection.
        """
        context_text = "\n\n".join(context_chunks) if context_chunks else None
        
        persona_config = config.PERSONAS.get(persona_mode, config.PERSONAS["Padrão (Neutro)"])
        
        tasks = []
        for i, model in enumerate(selected_models):
            # Determine system prompt for this specific model
            sys_prompt = None
            
            if "roles" in persona_config:
                # Assign roles in round-robin fashion
                role_desc = persona_config["roles"][i % len(persona_config["roles"])]
                sys_prompt = role_desc
            elif "system_prompt" in persona_config:
                sys_prompt = persona_config["system_prompt"]
                
            tasks.append(ModelCouncil.query_model(model, prompt, context_text, system_prompt=sys_prompt))
        
        results = await asyncio.gather(*tasks)
        
        # Inject the role into the result so we can display it?
        # For simplicty, we just return the result. Ideally we'd modify the response dict to include the role.
        # Let's post-process slightly if needed, but for now the content reflects the role.
        return results

    @staticmethod
    async def synthesize_answers(judge_model, prompt, model_results, council_mode="Padrão"):
        """
        Uses the judge model to synthesize the results.
        """
        # Format the responses for the judge
        responses_text = ""
        for res in model_results:
            if res['status'] == "Success":
                responses_text += f"## Response from {res['model']}:\n{res['response']}\n\n"
        
        if not responses_text:
            return "No successful responses to synthesize."

        synthesis_prompt = config.SYNTHESIS_PROMPT_TEMPLATE.format(
            user_prompt=prompt,
            model_responses=responses_text,
            council_mode=council_mode
        )

        try:
            client = ollama.AsyncClient()
            response = await client.generate(
                model=judge_model,
                prompt=synthesis_prompt,
                stream=False
            )
            return response['response']
        except Exception as e:
            return f"Error during synthesis: {str(e)}"
