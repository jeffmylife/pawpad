"""
Command-line interface for PawPad.
"""

import click
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

from .encoder import (
    generate_fingerprint,
    fingerprint_to_string,
    string_to_fingerprint,
    encode_fingerprint_in_text,
    detect_fingerprint_in_text,
    extract_fingerprint_from_text,
    encode_message_in_text,
    decode_message_from_text,
    encode_message_in_single_char,
    decode_message_from_single_char,
)

console = Console()


@click.group()
@click.version_option()
def main():
    """PawPad - Hide data in text using Unicode variation selectors.

    Supports two modes:
    • Fingerprinting: Watermark text with repeated fingerprints (encode/decode)
    • Messaging: Hide secret messages in text (hide/reveal)
    """
    pass


@main.command()
@click.option(
    "--text",
    "-t",
    prompt="Enter text to encode",
    help="Text to encode with fingerprint",
)
@click.option(
    "--fingerprint",
    "-f",
    help="Fingerprint to use (hex string). If not provided, a random one will be generated.",
)
@click.option(
    "--length", "-l", default=16, help="Length of fingerprint in bytes (default: 16)"
)
def encode(text: str, fingerprint: str, length: int):
    """Encode a fingerprint into text."""
    try:
        if fingerprint:
            fp_bytes = string_to_fingerprint(fingerprint)
        else:
            fp_bytes = generate_fingerprint(length)

        encoded_text = encode_fingerprint_in_text(text, fp_bytes)
        fp_string = fingerprint_to_string(fp_bytes)

        console.print(
            Panel(
                f"[bold green]Encoding successful![/bold green]\n\n"
                f"[bold]Original text:[/bold] {text}\n"
                f"[bold]Fingerprint:[/bold] {fp_string}\n"
                f"[bold]Encoded text:[/bold] {encoded_text}",
                title="Encode Result",
                border_style="green",
            )
        )

        # Also show the encoded text alone for easy copying
        console.print(f"\n[bold]Encoded text (copy this):[/bold]\n{encoded_text}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@main.command()
@click.option(
    "--text",
    "-t",
    prompt="Enter text to decode",
    help="Text to decode fingerprint from",
)
@click.option(
    "--fingerprint",
    "-f",
    help="Expected fingerprint (hex string). If provided, will check if this specific fingerprint is present.",
)
def decode(text: str, fingerprint: str):
    """Decode fingerprint from text."""
    try:
        if fingerprint:
            # Check for specific fingerprint
            expected_fp = string_to_fingerprint(fingerprint)
            is_present = detect_fingerprint_in_text(text, expected_fp)

            if is_present:
                console.print(
                    Panel(
                        f"[bold green]Fingerprint detected![/bold green]\n\n"
                        f"[bold]Text:[/bold] {text}\n"
                        f"[bold]Expected fingerprint:[/bold] {fingerprint}\n"
                        f"[bold]Result:[/bold] ✓ Present",
                        title="Detection Result",
                        border_style="green",
                    )
                )
            else:
                console.print(
                    Panel(
                        f"[bold red]Fingerprint not found![/bold red]\n\n"
                        f"[bold]Text:[/bold] {text}\n"
                        f"[bold]Expected fingerprint:[/bold] {fingerprint}\n"
                        f"[bold]Result:[/bold] ✗ Not present",
                        title="Detection Result",
                        border_style="red",
                    )
                )
        else:
            # Extract any fingerprint present
            extracted_fp = extract_fingerprint_from_text(text)

            if extracted_fp:
                fp_string = fingerprint_to_string(extracted_fp)
                console.print(
                    Panel(
                        f"[bold green]Fingerprint found![/bold green]\n\n"
                        f"[bold]Text:[/bold] {text}\n"
                        f"[bold]Extracted fingerprint:[/bold] {fp_string}",
                        title="Decode Result",
                        border_style="green",
                    )
                )
            else:
                console.print(
                    Panel(
                        f"[bold yellow]No fingerprint found![/bold yellow]\n\n"
                        f"[bold]Text:[/bold] {text}\n"
                        f"[bold]Result:[/bold] No hidden data detected",
                        title="Decode Result",
                        border_style="yellow",
                    )
                )

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@main.command()
@click.option(
    "--length", "-l", default=16, help="Length of fingerprint in bytes (default: 16)"
)
def generate(length: int):
    """Generate a random fingerprint."""
    try:
        fp_bytes = generate_fingerprint(length)
        fp_string = fingerprint_to_string(fp_bytes)

        console.print(
            Panel(
                f"[bold green]Generated fingerprint:[/bold green]\n\n"
                f"[bold]Hex string:[/bold] {fp_string}\n"
                f"[bold]Length:[/bold] {length} bytes",
                title="Generated Fingerprint",
                border_style="green",
            )
        )

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@main.command()
@click.option(
    "--text",
    "-t",
    prompt="Enter text to analyze",
    help="Text to analyze for hidden data",
)
def analyze(text: str):
    """Analyze text for hidden variation selectors."""
    try:
        # Create a table to show character analysis
        table = Table(title="Character Analysis")
        table.add_column("Character", style="cyan")
        table.add_column("Unicode", style="magenta")
        table.add_column("Hidden Data", style="green")
        table.add_column("Hex", style="yellow")

        found_any = False

        for i, char in enumerate(text):
            # Check if this character has hidden data
            hidden_data = extract_fingerprint_from_text(char)

            if hidden_data:
                found_any = True
                hex_data = fingerprint_to_string(hidden_data)
                table.add_row(char, f"U+{ord(char):04X}", "✓", hex_data)
            else:
                table.add_row(char, f"U+{ord(char):04X}", "✗", "")

        console.print(table)

        if found_any:
            console.print(
                f"\n[bold green]Hidden data detected in the text![/bold green]"
            )
        else:
            console.print(
                f"\n[bold yellow]No hidden data found in the text.[/bold yellow]"
            )

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@main.command()
@click.option(
    "--text",
    "-t",
    prompt="Enter text to encode message into",
    help="Text to encode secret message into",
)
@click.option(
    "--message",
    "-m",
    prompt="Enter secret message",
    help="Secret message to encode",
)
@click.option(
    "--single-char",
    "-s",
    is_flag=True,
    help="Encode entire message into a single character (Paul Butler's approach)",
)
def hide(text: str, message: str, single_char: bool):
    """Hide a secret message in text using variation selectors."""
    try:
        if single_char:
            if len(text) != 1:
                console.print(
                    "[bold red]Error:[/bold red] Single-char mode requires exactly one character as text"
                )
                sys.exit(1)
            encoded_text = encode_message_in_single_char(text, message)
        else:
            encoded_text = encode_message_in_text(text, message)

        console.print(
            Panel(
                f"[bold green]Message hidden successfully![/bold green]\n\n"
                f"[bold]Original text:[/bold] {text}\n"
                f"[bold]Secret message:[/bold] {message}\n"
                f"[bold]Encoded text:[/bold] {encoded_text}",
                title="Hide Message Result",
                border_style="green",
            )
        )

        # Also show the encoded text alone for easy copying
        console.print(f"\n[bold]Encoded text (copy this):[/bold]\n{encoded_text}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@main.command()
@click.option(
    "--text",
    "-t",
    prompt="Enter text to reveal message from",
    help="Text to decode secret message from",
)
@click.option(
    "--single-char",
    "-s",
    is_flag=True,
    help="Decode message from a single character (Paul Butler's approach)",
)
def reveal(text: str, single_char: bool):
    """Reveal a secret message hidden in text."""
    try:
        if single_char:
            decoded_message = decode_message_from_single_char(text)
        else:
            decoded_message = decode_message_from_text(text)

        if decoded_message:
            console.print(
                Panel(
                    f"[bold green]Secret message found![/bold green]\n\n"
                    f"[bold]Text:[/bold] {text}\n"
                    f"[bold]Hidden message:[/bold] {decoded_message}",
                    title="Reveal Message Result",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    f"[bold yellow]No secret message found![/bold yellow]\n\n"
                    f"[bold]Text:[/bold] {text}\n"
                    f"[bold]Result:[/bold] No hidden message detected",
                    title="Reveal Message Result",
                    border_style="yellow",
                )
            )

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
