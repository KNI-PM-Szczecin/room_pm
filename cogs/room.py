import nextcord
from utilities import baseUtils
from nextcord.ext import commands
from utilities.find_room import RoomFinder

class RoomCog(commands.Cog):
    def __init__(self, client, config: baseUtils.ConfigReader):
        self.client = client
        self.config = config

        self.roomFinder = RoomFinder(URL=config.get_supabase_url(), KEY=config.get_supabase_key())

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
        name="znajdz_pokoj",
        description="Szukaj wolnego pokoju",
    )
    async def find_room(self,
        interaction: nextcord.Interaction,
        building: str = nextcord.SlashOption(
            name="budynek",
            description="Wybierz budynek",
            required=True,
            choices={
                "Willowa": "Willowa",
                "Willowa B1": "Willowa B1",
                "Willowa B2": "Willowa B2",
                "Willowa B4": "Willowa B4",
                "W. Chrobrego": "WChrobrego",
                "H. Pobożnego": "HPobożnego",
                "Szczerbcowa": "Szczerbcow",
                "Żołnierska": "Żołnierska"
            }
        ),
        day: int = nextcord.SlashOption(
            name= "dzien",
            description="Wybierz dzień (0-31)",
            min_value=0,
            max_value=31,
            required=True
        ),
        month: int = nextcord.SlashOption(
          name = "miesiac",
            description="Wybierz miesiąc (1-12)",
            min_value=1,
            max_value=12,
            required=True
        ),
        year: str = nextcord.SlashOption(
            name = "rok",
            description="Wybierz rok, (można skrócić np. 7 27, 027 -> 2027)",
            required=False
        )):
        await interaction.response.send_message(f"Szukam pokoju w {building} na dzień {day}:{month}:{year}...")

        day = baseUtils.ZeroNum(str(day))
        month = baseUtils.ZeroNum(str(month))
        year = baseUtils.ShortYear(year)
        date = f"{day}-{month}-{year}"

        view = self.HourSelectView()
        await view.wait()

        hours = [baseUtils.HoursConverter(i)[0] for i in view.selected_hours]
        rooms = baseUtils.ListCommon([self.roomFinder.findEmptyRooms(f"{date} {h}", building) for h in hours])


        if view.selected_hours:
            final_content = (
                f"**Data:** {date}\n"
                f"**Wybrane godziny:** {view.selected_hours}\n"
                f"**Dostępne sale:** {rooms}"
            )

            await interaction.edit_original_message(
                content=final_content,
                view=None
            )