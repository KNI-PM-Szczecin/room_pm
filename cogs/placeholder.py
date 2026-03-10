import nextcord
from nextcord.ext import commands
from utilities import baseUtils

class PlaceholderCog(commands.Cog):
    def __init__(self, client, config: baseUtils.ConfigReader):
        self.client = client
        self.config = config

    class HourSelectView(nextcord.ui.View):
        def __init__(self):
            super().__init__(timeout=60)
            self.selected_hours = []

        @nextcord.ui.string_select(
            placeholder="Wybierz godziny (1-14)...",
            min_values=1,
            max_values=14,
            options=[
                nextcord.SelectOption(label=f"Godzina {i}", value=str(i)) for i in range(1, 15)
            ]
        )
        async def select_callback(self, select: nextcord.ui.StringSelect, interaction: nextcord.Interaction):
            self.selected_hours = [int(h) for h in select.values]
            await interaction.response.defer()
            self.stop()

    @nextcord.slash_command(
        name="znajdz_sale",
        description="Demo",
    )
    async def znajdz_sale(
            self,
            interaction: nextcord.Interaction,
            data: str = nextcord.SlashOption(description="Wprowadź datę (format: DD.MM.YYYY)", required=True)
    ):
        view = self.HourSelectView()

        await interaction.response.send_message(
            f"Wybrałeś datę: **{data}**.\nWybierz teraz godziny z listy poniżej:",
            view=view,
            ephemeral=True
        )

        await view.wait()

        if view.selected_hours:
            final_content = (
                f"**Data:** {data}\n"
                f"**Wybrane godziny:** {view.selected_hours}\n"
                f"**Dostępne sale:** 172, 180, 19, aula Łaskiego"
            )

            await interaction.edit_original_message(
                content=final_content,
                view=None
            )