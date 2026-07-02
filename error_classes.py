class ParserError(Exception):
    """
    Base exception for malformed or invalid entries in the map definition file
    (nb_drones, hub, connection, formatting, etc.). Typically raised with
    (line_number, message) as args.
    """
    pass


class HubMetadataError(ParserError):
    """
    Raised when a hub's metadata block (zone/color/max_drones) is malformed or
    contains an invalid value.
    """
    pass


class ConnectionEdgError(ParserError):
    """
    Raised when a connection's edge definition ('src-dest') is malformed.
    """
    pass


class ConnectionMetadataError(ParserError):
    """
    Raised when a connection's metadata block (max_link_capacity) is malformed
    or contains an invalid value.
    """
    pass


class HubFormatError(ParserError):
    """
    Raised when a hub definition line doesn't match the expected
    'name x y [metadata]' format, including duplicate names or coordinates.
    """
    pass


class Grapherror(Exception):
    """
    Raised for structural problems in the parsed graph, such as an unreachable
    end hub or a disconnected hub.
    """
    pass


class Errors:
    no_path_emogi = """
    ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⣴⡟⠻⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⡟⠛⢟⣷⡄⠀⠀
⣿⣅⣶⠿⠻⣷⡀⠀⠀⠀⠀⣠⣤⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢳⣼⠿⣿⣧⣄⠀
⠻⣆⡏⠀⢀⣼⣷⣦⣄⢠⣾⠋⠘⢙⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀       ⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣀⡀⠀⠀⢈⡿⡄⠀⢣⢹⡄
⠀⠙⡇⢰⠟⠁⠰⠲⡝⡿⠉⠀⣠⡾⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣼⣿⣵⣶⣶⠿⣿⣶⣤⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠟⠫⢿⡆⠀⢸⣷⢧⡠⣬⡼⠃
⠀⠀⢇⡞⠀⠀⣰⠷⠛⠁⠀⢰⡏⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣾⣿⠟⠉⠠⠀⠤⠠⣐⣯⠽⠍⠻⢗⣦⣄⠀⠀⠀⠀⠀⠀⠻⣦⠀⠙⡇⣰⡿⣯⠃⠉⢪⢻⡄
⠀⠀⠸⣇⠀⢠⡇⠀⠀⠀⠀⣾⠀⠀⠀⠀⠀⠀⠀⢠⡾⢋⣿⣷⠟⣻⠟⠃⠀⠀⠀⠻⣿⢿⣶⣤⡀⠑⠈⢳⣄⠀⠀⠀⠀⠀⢸⠀⢤⠷⠋⠀⠉⡿⡜⠀⢹⡯
⠀⠀⠀⢹⡆⠈⠁⢠⣦⡀⠀⢻⠀⠀⠀⠀⠀⠀⣴⠏⢰⡿⠋⠠⠴⠋⣀⣀⣀⣤⣀⣀⡈⠛⠈⠩⠻⠀⠀⠀⠙⣧⠀⠀⠀⠀⢸⠂⣤⡶⠀⠀⠸⠁⠀⢀⣼⠃
⠀⠀⠀⠈⢷⡀⠀⠈⢣⡹⣦⣾⠀⠀⠀⠀⠀⣼⠁⠀⠀⠀⠀⠀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣷⣤⡀⠀⠀⠀⠀⠀⢈⣧⡀⠀⠀⢸⣄⣿⠀⠀⠀⠀⠀⣠⡞⠃⠀
⠀⠀⠀⠀⠈⠻⣆⣀⣀⣡⡟⠀⠀⠀⠀⠀⣼⢣⠀⠀⠀⠀⢀⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⡄⠀⠀⠀⠀⠈⡝⣇⠀⠀⠀⠙⢿⣖⣀⣀⣤⠞⠉⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠉⠉⠉⠀⠀⠀⠀⠀⢰⣿⡎⠀⠀⠀⢠⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⠀⠀⠀⠀⢹⢻⡄⠀⠀⠀⠀⠉⠉⠉⠁⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⡗⠀⠀⢀⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡄⠀⠀⠀⠈⡎⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡇⠃⠀⠀⣸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⠀⠀⠀⠘⢀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣗⡆⠀⢰⣿⣿⣿⣿⣿⣿⠿⠋⠉⠉⠉⠙⢿⣿⣿⣿⣿⣿⣿⡇⠀⠀⢰⢸⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⠱⠀⣸⣿⣿⣿⣿⠿⠁⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⣿⣿⣿⣿⠀⠀⠌⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣷⠀⣿⣿⣿⣿⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣿⣿⣿⣿⡇⢀⣼⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⢀⠿⡿⠟⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠿⣿⡿⠃⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣦⣆⣰⠟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⣄⡀⣀⣸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠛⠉⠳⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⠞⠛⠶⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠳⠦⠤⢄⣀⣀⣀⣀⡠⡤⠶⠛⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠉⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    """

    @staticmethod
    def display_error(error: Exception, filepath: str = "") -> None:
        from rich.console import Console
        from rich.syntax import Syntax
        from rich.markup import escape
        from rich.panel import Panel

        console = Console()
        console.print()
        if isinstance(error, ParserError) or isinstance(error, Grapherror):
            line_number, error_msg = error.args
            if isinstance(error, ParserError):
                title = "ParserError Error in Line"
            else:
                title = "Graph Error"

            if "No valid path exists" in error_msg:

                panel = Panel(
                    f"[bold yellow]{Errors.no_path_emogi}[/bold yellow]",
                    padding=(0, 50),
                    border_style="red",
                    title=title,
                )

                console.print(panel)
                console.print(f"[red]{escape(error_msg)}[/red]")

            else:
                console.print(
                    Panel(
                        Syntax.from_path(
                            filepath,
                            line_numbers=True,
                            highlight_lines={line_number},
                            line_range=(
                                max(1, line_number - 4),
                                line_number + 4
                            ),
                            theme="ansi_dark",
                        ),
                        title="[bold red]Traceback[/bold red]",
                        border_style="red",
                    )
                )
                console.print(
                    f"[bold red]{title} [{line_number}]:"
                    f"[/bold red]\n[red]{escape(error_msg)}[/red]"
                )
                console.print()
        else:
            console.print(f"[bold red]{str(error)}[/bold red]")
