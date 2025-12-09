import requests
import json
from typing import Any, Dict, List, Optional
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.base_toolset import BaseToolset
from google.adk.tools.function_tool import FunctionTool

class SrMcpToolset(BaseToolset):
    """Tools for accessing Sveriges Radio MCP Server."""

    def __init__(self):
        super().__init__()
        self.url = "https://sveriges-radio.onrender.com/mcp"

    def _call_mcp(self, tool_name: str, params: Dict[str, Any]) -> Any:
        # Remove self and None values
        clean_params = {k: v for k, v in params.items() if k != 'self' and v is not None}
        payload = {
            "jsonrpc": "2.0",
            "method": f"tools/call",
            "id": 1,
            "params": {
                "name": tool_name,
                "arguments": clean_params
            }
        }
        try:
            response = requests.post(self.url, json=payload)
            response.raise_for_status()
            result = response.json()
            if "error" in result:
                return f"Error from MCP: {result['error']}"
            # MCP returns {content: [{type: 'text', text: ...}]} usually
            # But let's return the whole result field or parse it.
            return result.get("result", {})
        except Exception as e:
            return f"Error calling MCP tool {tool_name}: {e}"

    def list_channels(self, channelId: Optional[float] = None, channelType: Optional[str] = None, audioQuality: Optional[str] = None, pagination: Optional[bool] = None, page: Optional[float] = None, size: Optional[float] = None) -> Any:
        """Lista alla radiokanaler från Sveriges Radio (P1, P2, P3, P4, lokala kanaler). Inkluderar live stream-länkar och kanalinformation."""
        return self._call_mcp("list_channels", locals())

    def get_channel_rightnow(self, channelId: Optional[float] = None, sortBy: Optional[str] = None) -> Any:
        """Visa vad som sänds JUST NU på Sveriges Radio. Kan visa en specifik kanal eller alla kanaler samtidigt med föregående, nuvarande och nästa program."""
        return self._call_mcp("get_channel_rightnow", locals())

    def search_programs(self, query: Optional[str] = None, programCategoryId: Optional[float] = None, channelId: Optional[float] = None, hasOnDemand: Optional[bool] = None, isArchived: Optional[bool] = None, sort: Optional[str] = None, page: Optional[float] = None, size: Optional[float] = None, format: Optional[str] = None) -> Any:
        """Sök efter radioprogram i Sveriges Radio. Söker i programnamn med relevansranking. TIPS: För bättre resultat, använd programCategoryId eller channelId som filter. Exempel: channelId=164 för P3-program, programCategoryId=82 för dokumentärer."""
        return self._call_mcp("search_programs", locals())

    def get_program(self, programId: Optional[float] = None, format: Optional[str] = None) -> Any:
        """Hämta detaljerad information om ett specifikt radioprogram inklusive beskrivning, kanal, kontaktinfo och poddgrupper."""
        return self._call_mcp("get_program", locals())

    def list_program_categories(self, categoryId: Optional[float] = None, page: Optional[float] = None, size: Optional[float] = None, format: Optional[str] = None) -> Any:
        """Lista alla programkategorier i Sveriges Radio (t.ex. Nyheter, Musik, Sport, Kultur, Samhälle) eller hämta en specifik kategori."""
        return self._call_mcp("list_program_categories", locals())

    def get_program_schedule(self, programId: Optional[float] = None, fromDate: Optional[str] = None, toDate: Optional[str] = None, page: Optional[float] = None, size: Optional[float] = None, format: Optional[str] = None) -> Any:
        """Hämta tablå/schema för ett specifikt program - när det sänds och på vilka kanaler."""
        return self._call_mcp("get_program_schedule", locals())

    def list_broadcasts(self, programId: Optional[float] = None, page: Optional[float] = None, size: Optional[float] = None, format: Optional[str] = None) -> Any:
        """Lista alla tillgängliga sändningar för ett specifikt program. Sändningar är tillgängliga i 30 dagar efter publicering."""
        return self._call_mcp("list_broadcasts", locals())

    def list_podfiles(self, programId: Optional[float] = None, page: Optional[float] = None, size: Optional[float] = None, format: Optional[str] = None) -> Any:
        """Lista alla tillgängliga poddfiler för ett specifikt program. Returnerar poddfilernas metadata inklusive URL för nedladdning."""
        return self._call_mcp("list_podfiles", locals())

    def get_podfile(self, podfileId: Optional[float] = None, format: Optional[str] = None) -> Any:
        """Hämta en specifik poddfil med fullständig information inklusive URL, storlek, längd och publiceringsdatum."""
        return self._call_mcp("get_podfile", locals())

    def list_episodes(self, programId: Optional[float] = None, fromDate: Optional[str] = None, toDate: Optional[str] = None, audioQuality: Optional[str] = None, page: Optional[float] = None, size: Optional[float] = None, format: Optional[str] = None) -> Any:
        """Lista alla avsnitt för ett radioprogram. Kan filtrera på datumintervall och välja ljudkvalitet."""
        return self._call_mcp("list_episodes", locals())

    def search_episodes(self, query: Optional[str] = None, channelId: Optional[float] = None, programId: Optional[float] = None, page: Optional[float] = None, size: Optional[float] = None, format: Optional[str] = None) -> Any:
        """Fulltextsök i avsnitt från Sveriges Radio. Sök i titlar, beskrivningar och innehåll."""
        return self._call_mcp("search_episodes", locals())

    def get_episode(self, episodeId: Optional[float] = None, audioQuality: Optional[str] = None, format: Optional[str] = None) -> Any:
        """Hämta ett specifikt avsnitt med fullständig information inklusive ljudfiler för streaming och nedladdning."""
        return self._call_mcp("get_episode", locals())

    def get_episodes_batch(self, episodeIds: Optional[str] = None, audioQuality: Optional[str] = None, format: Optional[str] = None) -> Any:
        """Hämta flera avsnitt samtidigt i ett anrop (effektivt för att hämta flera episoder)."""
        return self._call_mcp("get_episodes_batch", locals())

    def get_latest_episode(self, programId: Optional[float] = None, audioQuality: Optional[str] = None, format: Optional[str] = None) -> Any:
        """Hämta det senaste avsnittet för ett program (användbart för att alltid få det nyaste)."""
        return self._call_mcp("get_latest_episode", locals())

    def get_channel_schedule(self, channelId: Optional[float] = None, date: Optional[str] = None, page: Optional[float] = None, size: Optional[float] = None, format: Optional[str] = None) -> Any:
        """Hämta tablå (TV guide-style) för en radiokanal på ett specifikt datum. Visar kronologiskt vad som sänds hela dagen."""
        return self._call_mcp("get_channel_schedule", locals())

    def get_program_broadcasts(self, programId: Optional[float] = None, fromDate: Optional[str] = None, toDate: Optional[str] = None, page: Optional[float] = None, size: Optional[float] = None, format: Optional[str] = None) -> Any:
        """Hämta kommande sändningar för ett specifikt program. Se när programmet sänds framöver."""
        return self._call_mcp("get_program_broadcasts", locals())

    def get_all_rightnow(self, channelId: Optional[float] = None, sortBy: Optional[str] = None, page: Optional[float] = None, size: Optional[float] = None, format: Optional[str] = None) -> Any:
        """Översikt av vad som sänds JUST NU på ALLA Sveriges Radio-kanaler samtidigt (eller en specifik kanal). Perfekt för att se vad som finns att lyssna på."""
        return self._call_mcp("get_all_rightnow", locals())

    def get_playlist_rightnow(self, channelId: Optional[float] = None, format: Optional[str] = None) -> Any:
        """Hämta låt som spelas JUST NU på en kanal. Returnerar föregående låt, nuvarande låt och nästkommande låt med fullständig information (artist, titel, album, skivbolag, kompositör, producent, textförfattare, tidsstämplar)."""
        return self._call_mcp("get_playlist_rightnow", locals())

    def get_channel_playlist(self, channelId: Optional[float] = None, startDateTime: Optional[str] = None, endDateTime: Optional[str] = None, size: Optional[float] = None, page: Optional[float] = None, format: Optional[str] = None) -> Any:
        """Hämta alla låtar som spelats i en kanal under ett tidsintervall. Perfekt för att se musikhistorik på en kanal mellan två datum. Returnerar titel, artist, kompositör, album, skivbolag, och tidsstämplar för varje låt."""
        return self._call_mcp("get_channel_playlist", locals())

    def get_program_playlist(self, programId: Optional[float] = None, startDateTime: Optional[str] = None, endDateTime: Optional[str] = None, size: Optional[float] = None, page: Optional[float] = None, format: Optional[str] = None) -> Any:
        """Hämta alla låtar som spelats i ett program under ett tidsintervall. Använd detta för att få musikhistorik för ett specifikt program mellan två datum. Inkluderar alla låtdetaljer."""
        return self._call_mcp("get_program_playlist", locals())

    def get_episode_playlist(self, episodeId: Optional[float] = None, format: Optional[str] = None) -> Any:
        """Hämta komplett spellista för ett specifikt programavsnitt (episode). Listar alla låtar som spelades i avsnittet med fullständiga detaljer och tidsstämplar."""
        return self._call_mcp("get_episode_playlist", locals())

    def list_news_programs(self, page: Optional[float] = None, size: Optional[float] = None, format: Optional[str] = None) -> Any:
        """Lista alla nyhetsprogram från Sveriges Radio (Ekot, Ekonomiekot, Kulturnytt, P4 Nyheter, etc.)."""
        return self._call_mcp("list_news_programs", locals())

    def get_latest_news_episodes(self, page: Optional[float] = None, size: Optional[float] = None, format: Optional[str] = None) -> Any:
        """Hämta senaste nyhetsavsnitt från alla nyhetsprogram (max 1 dag gamla). Perfekt för en snabb nyhetsöversikt!"""
        return self._call_mcp("get_latest_news_episodes", locals())

    def get_traffic_messages(self, trafficAreaName: Optional[str] = None, date: Optional[str] = None, page: Optional[float] = None, size: Optional[float] = None, format: Optional[str] = None) -> Any:
        """Hämta trafikmeddelanden (olyckor, köer, störningar) från Sveriges Radio. Kan filtrera på område och datum. Priority: 1=Mycket allvarlig, 5=Mindre störning."""
        return self._call_mcp("get_traffic_messages", locals())

    def get_traffic_areas(self, latitude: Optional[float] = None, longitude: Optional[float] = None, page: Optional[float] = None, size: Optional[float] = None, format: Optional[str] = None) -> Any:
        """Hämta trafikområden. Kan användas med GPS-koordinater för att hitta vilket område en position tillhör, eller utan parametrar för att lista alla områden."""
        return self._call_mcp("get_traffic_areas", locals())

    def get_recently_published(self, audioQuality: Optional[str] = None, page: Optional[float] = None, size: Optional[float] = None) -> Any:
        """Hämta senast publicerade sändningar och poddar från Sveriges Radio. Perfekt för att se vad som är nytt!"""
        return self._call_mcp("get_recently_published", locals())

    def get_top_stories(self, programId: Optional[float] = None) -> Any:
        """Hämta toppuffar (featured content) från Sveriges Radio. Kan hämta från SR:s förstasida eller ett specifikt program."""
        return self._call_mcp("get_top_stories", locals())

    def list_extra_broadcasts(self, date: Optional[str] = None, sort: Optional[str] = None, page: Optional[float] = None, size: Optional[float] = None) -> Any:
        """Lista extrasändningar (sport, special events) från Sveriges Radio."""
        return self._call_mcp("list_extra_broadcasts", locals())

    def get_episode_group(self, groupId: Optional[float] = None, page: Optional[float] = None, size: Optional[float] = None) -> Any:
        """Hämta en grupp/samling av avsnitt (t.ex. "Kända kriminalfall", "Sommarens bästa dokumentärer")."""
        return self._call_mcp("get_episode_group", locals())

    def search_all(self, query: Optional[str] = None, searchIn: Optional[str] = None, limit: Optional[float] = None) -> Any:
        """Global sökning över program, avsnitt och kanaler samtidigt. Perfekt för att hitta innehåll när du inte vet exakt var det finns!"""
        return self._call_mcp("search_all", locals())

    def list_ondemand_audio_templates(self) -> Any:
        """Hämta URL-mallar för on-demand-ljud (podcast/avsnitt). Mallarna visar hur ljudlänkar är uppbyggda med platshållare som [quality] och [audioId]."""
        return self._call_mcp("list_ondemand_audio_templates", locals())

    def list_live_audio_templates(self) -> Any:
        """Hämta URL-mallar för live-ljud (direktsändning). Mallarna visar hur ljudlänkar är uppbyggda med platshållare som [quality] och [channelid]."""
        return self._call_mcp("list_live_audio_templates", locals())

    async def get_tools(self, readonly_context=None) -> List[BaseTool]:
        return [
            FunctionTool(self.list_channels),
            FunctionTool(self.get_channel_rightnow),
            FunctionTool(self.search_programs),
            FunctionTool(self.get_program),
            FunctionTool(self.list_program_categories),
            FunctionTool(self.get_program_schedule),
            FunctionTool(self.list_broadcasts),
            FunctionTool(self.list_podfiles),
            FunctionTool(self.get_podfile),
            FunctionTool(self.list_episodes),
            FunctionTool(self.search_episodes),
            FunctionTool(self.get_episode),
            FunctionTool(self.get_episodes_batch),
            FunctionTool(self.get_latest_episode),
            FunctionTool(self.get_channel_schedule),
            FunctionTool(self.get_program_broadcasts),
            FunctionTool(self.get_all_rightnow),
            FunctionTool(self.get_playlist_rightnow),
            FunctionTool(self.get_channel_playlist),
            FunctionTool(self.get_program_playlist),
            FunctionTool(self.get_episode_playlist),
            FunctionTool(self.list_news_programs),
            FunctionTool(self.get_latest_news_episodes),
            FunctionTool(self.get_traffic_messages),
            FunctionTool(self.get_traffic_areas),
            FunctionTool(self.get_recently_published),
            FunctionTool(self.get_top_stories),
            FunctionTool(self.list_extra_broadcasts),
            FunctionTool(self.get_episode_group),
            FunctionTool(self.search_all),
            FunctionTool(self.list_ondemand_audio_templates),
            FunctionTool(self.list_live_audio_templates),
        ]