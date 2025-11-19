"""
Cyberpunk UI Utilities - Styling, animations, and effects
"""
import asyncio
import random
from typing import Optional, List


class CyberpunkUI:
    """Cyberpunk-themed UI elements and animations"""

    # Leet speak character mappings
    LEET_MAP = {
        'a': ['4', '@', 'Д'],
        'e': ['3', '€', 'ë'],
        'i': ['1', '!', '|'],
        'o': ['0', 'Ø', '°'],
        's': ['5', '$', '§'],
        't': ['7', '+', '†'],
        'l': ['1', '|', '£'],
        'g': ['9', '6'],
        'b': ['8', 'ß'],
        'z': ['2'],
    }

    # ASCII art templates
    ASCII_LOGO = """
╔═══════════════════════════════╗
║  ██████╗ ██╗   ██╗███████╗██╗ ║
║  ██╔══██╗██║   ██║██╔════╝██║ ║
║  ██████╔╝██║   ██║███████╗██║ ║
║  ██╔═══╝ ██║   ██║╚════██║██║ ║
║  ██║     ╚██████╔╝███████║██║ ║
║  ╚═╝      ╚═════╝ ╚══════╝╚═╝ ║
║      [ PUSHTUTOR v2.0 ]       ║
║    [:: CYBERSPACE EDITION ::]  ║
╚═══════════════════════════════╝
"""

    ASCII_SKULL = """
    ░░░░░░░░░▄▄▄▄▄
    ░░░░░░░░▀▀▀██████▄▄▄
    ░░░░░░▄▄▄▄▄░░█████████▄
    ░░░░░▀▀▀▀█████▌░▀▐▄░▀▐█
    ░░░▀▀█████▄▄░▀██████▄██
    ░░░▀▄▄▄▄▄░░▀▀█▄▀█════█▀
    ░░░░░░░░▀▀▀▄░░▀▀███░▀░░░░░░▄▄
    ░░░░░▄███▀▀██▄████████▄░▄▀▀▀██▌
    ░░░██▀▄▄▄██▀▄███▀▀▀▀████░░░░░▀█▄
    ▄▀▀▀▄██▄▀▀▌█████████████░░░░▌▄▄▀
    ▌░░░░▐▀████▐███████████▌
    ▀▄░░▄▀░░░▀▀████████████▀
    ░░▀▀░░░░░░▀▀█████████▀
    ░░░░░░░░▄▄██▀██████▀█
    ░░░░░░▄██▀░░░░░▀▀▀░░█
    ░░░░░▄█░░░░░░░░░░░░░▐▌
    ░▄▄▄▄█▌░░░░░░░░░░░░░░▀█▄▄▄▄▀▀▄
    ▌░░░░░▐░░░░░░░░░░░░░░░░▀▀▄▄▄▀
    """

    GLITCH_CHARS = ['█', '▓', '▒', '░', '▀', '▄', '▌', '▐', '■']

    # Progress bar styles
    PROGRESS_STYLES = {
        'cyber': {
            'filled': '█',
            'empty': '░',
            'start': '[',
            'end': ']',
        },
        'glitch': {
            'filled': '▓',
            'empty': '░',
            'start': '【',
            'end': '】',
        },
        'neon': {
            'filled': '━',
            'empty': '─',
            'start': '╾',
            'end': '╼',
        },
    }

    @staticmethod
    def to_leet(text: str, intensity: float = 0.5) -> str:
        """
        Convert text to leet speak

        Args:
            text: Input text
            intensity: 0.0-1.0, how much to convert (0.5 = 50% of applicable chars)

        Returns:
            Leet speak text
        """
        result = []
        for char in text:
            lower_char = char.lower()
            if lower_char in CyberpunkUI.LEET_MAP and random.random() < intensity:
                leet_char = random.choice(CyberpunkUI.LEET_MAP[lower_char])
                # Preserve original case tendency
                result.append(leet_char)
            else:
                result.append(char)

        return ''.join(result)

    @staticmethod
    def glitch_text(text: str, intensity: int = 3) -> str:
        """
        Add glitch effect to text

        Args:
            text: Input text
            intensity: Number of glitch characters to add

        Returns:
            Glitched text
        """
        if not text:
            return text

        result = text
        for _ in range(intensity):
            pos = random.randint(0, len(result))
            glitch_char = random.choice(CyberpunkUI.GLITCH_CHARS)
            result = result[:pos] + glitch_char + result[pos:]

        return result

    @staticmethod
    def create_progress_bar(progress: float, width: int = 20,
                           style: str = 'cyber', show_percent: bool = True) -> str:
        """
        Create a progress bar

        Args:
            progress: 0.0-1.0
            width: Bar width in characters
            style: 'cyber', 'glitch', or 'neon'
            show_percent: Show percentage text

        Returns:
            Progress bar string
        """
        style_config = CyberpunkUI.PROGRESS_STYLES.get(style, CyberpunkUI.PROGRESS_STYLES['cyber'])

        filled_width = int(width * progress)
        empty_width = width - filled_width

        bar = (
            style_config['start'] +
            style_config['filled'] * filled_width +
            style_config['empty'] * empty_width +
            style_config['end']
        )

        if show_percent:
            bar += f" {int(progress * 100)}%"

        return bar

    @staticmethod
    def create_box(text: str, title: str = None, style: str = 'double') -> str:
        """
        Create a text box

        Args:
            text: Content
            title: Optional title
            style: 'single', 'double', 'cyber'

        Returns:
            Boxed text
        """
        lines = text.split('\n')
        max_width = max(len(line) for line in lines) if lines else 0

        if style == 'double':
            top = '╔' + '═' * (max_width + 2) + '╗'
            bottom = '╚' + '═' * (max_width + 2) + '╝'
            side = '║'
        elif style == 'cyber':
            top = '┏' + '━' * (max_width + 2) + '┓'
            bottom = '┗' + '━' * (max_width + 2) + '┛'
            side = '┃'
        else:  # single
            top = '┌' + '─' * (max_width + 2) + '┐'
            bottom = '└' + '─' * (max_width + 2) + '┘'
            side = '│'

        result = [top]

        if title:
            title_line = f"{side} {title.center(max_width)} {side}"
            result.append(title_line)
            result.append(top.replace('╔', '╠').replace('╗', '╣'))

        for line in lines:
            result.append(f"{side} {line.ljust(max_width)} {side}")

        result.append(bottom)

        return '\n'.join(result)

    @staticmethod
    async def typing_animation(text: str, delay: float = 0.05) -> List[str]:
        """
        Generate typing animation frames

        Args:
            text: Text to type
            delay: Delay between characters

        Returns:
            List of progressive text states
        """
        frames = []
        current = ""

        for char in text:
            current += char
            frames.append(current + "▌")  # Cursor
            await asyncio.sleep(delay)

        frames.append(text)  # Final without cursor
        return frames

    @staticmethod
    def create_welcome_message(username: str = None) -> str:
        """Create cyberpunk welcome message"""
        user_tag = username or "us3r"

        welcome = f"""
{CyberpunkUI.ASCII_LOGO}

> SYS INIT... OK
> LOADING NEURAL INTERFACE... OK
> CONNECTING TO CYBERSPACE... OK

╔════════════════════════════════╗
║  W3LC0M3 T0 TH3 M4TR1X, {user_tag[:10].upper().ljust(10)}  ║
╚════════════════════════════════╝

» Type /h3lp for command list
» Type /s34rch to search the archive
» Type /ch4nn3ls for indexed channels

[ SYSTEM STATUS: ONLINE ]
[ NEURAL LINK: ACTIVE ]
[ SECURITY: ENCRYPTED ]

> Ready to jack in...
"""
        return welcome

    @staticmethod
    def create_loading_message(task: str = "Processing") -> str:
        """Create loading message"""
        frames = [
            f"⣾ {task}...",
            f"⣽ {task}...",
            f"⣻ {task}...",
            f"⢿ {task}...",
            f"⡿ {task}...",
            f"⣟ {task}...",
            f"⣯ {task}...",
            f"⣷ {task}...",
        ]
        return random.choice(frames)

    @staticmethod
    def create_search_header() -> str:
        """Create search results header"""
        return """
╔══════════════════════════════════╗
║  [S34RCH R3SU£75]               ║
║  > Scanning database...          ║
╚══════════════════════════════════╝
"""

    @staticmethod
    def format_search_result(result_num: int, channel_name: str,
                            message_snippet: str, date: str = None) -> str:
        """Format a search result"""
        snippet = message_snippet[:100] + "..." if len(message_snippet) > 100 else message_snippet

        date_str = f"[{date}]" if date else ""

        return f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ #{result_num} » {channel_name}
┃ {date_str}
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ {snippet}
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
"""

    @staticmethod
    def create_glass_button_markup(buttons: List[List[dict]]) -> dict:
        """
        Create inline keyboard markup with glass-morphism style

        Args:
            buttons: List of button rows, each row is list of {'text': str, 'callback_data': str}

        Returns:
            Telegram inline keyboard markup dict
        """
        # Add visual indicators to buttons
        styled_buttons = []
        for row in buttons:
            styled_row = []
            for btn in row:
                text = btn.get('text', '')
                # Add cyberpunk styling
                styled_text = f"『{text}』"
                styled_row.append({
                    'text': styled_text,
                    'callback_data': btn.get('callback_data', ''),
                    **{k: v for k, v in btn.items() if k not in ['text', 'callback_data']}
                })
            styled_buttons.append(styled_row)

        return {'inline_keyboard': styled_buttons}

    @staticmethod
    def create_stats_display(stats: dict) -> str:
        """Display statistics in cyberpunk style"""
        stats_lines = []

        for key, value in stats.items():
            key_formatted = key.replace('_', ' ').upper()
            stats_lines.append(f"  {key_formatted.ljust(20)}: {value}")

        return CyberpunkUI.create_box(
            '\n'.join(stats_lines),
            title="[[ STATISTICS ]]",
            style='cyber'
        )


# Create global instance
ui = CyberpunkUI()
