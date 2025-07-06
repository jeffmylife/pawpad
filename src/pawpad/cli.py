"""
Command-line interface for PawPad.
"""

import click
import sys
import os
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
    # Cryptographic functions
    generate_key_pair,
    save_key_pair,
    load_private_key,
    load_public_key,
    sign_text_with_chained_fingerprints,
    verify_chained_fingerprints,
    extract_original_text_from_signed,
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
    help="Text to encode with fingerprint",
)
@click.option(
    "--input-file",
    "-i",
    type=click.Path(exists=True),
    help="Read text from file instead of --text option",
)
@click.option(
    "--output-file",
    "-o",
    type=click.Path(),
    help="Write encoded text to file",
)
@click.option(
    "--fingerprint",
    "-f",
    help="Fingerprint to use (hex string). If not provided, a random one will be generated.",
)
@click.option(
    "--length", "-l", default=16, help="Length of fingerprint in bytes (default: 16)"
)
def encode(text: str, input_file: str, output_file: str, fingerprint: str, length: int):
    """Encode a fingerprint into text."""
    try:
        # Get input text
        if input_file:
            with open(input_file, "r", encoding="utf-8") as f:
                text = f.read().strip()
        elif not text:
            text = click.prompt("Enter text to encode")

        if fingerprint:
            fp_bytes = string_to_fingerprint(fingerprint)
        else:
            fp_bytes = generate_fingerprint(length)

        encoded_text = encode_fingerprint_in_text(text, fp_bytes)
        fp_string = fingerprint_to_string(fp_bytes)

        # Output results
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(encoded_text)
            console.print(f"[green]✓[/green] Encoded text written to: {output_file}")

        console.print(
            Panel(
                f"[bold green]Encoding successful![/bold green]\n\n"
                f"[bold]Original text:[/bold] {text}\n"
                f"[bold]Fingerprint:[/bold] {fp_string}\n"
                f"[bold]Encoded text:[/bold] {encoded_text if not output_file else f'(written to {output_file})'}",
                title="Encode Result",
                border_style="green",
            )
        )

        # Also show the encoded text alone for easy copying if not writing to file
        if not output_file:
            console.print(f"\n[bold]Encoded text (copy this):[/bold]\n{encoded_text}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@main.command()
@click.option(
    "--text",
    "-t",
    help="Text to decode fingerprint from",
)
@click.option(
    "--input-file",
    "-i",
    type=click.Path(exists=True),
    help="Read text from file instead of --text option",
)
@click.option(
    "--fingerprint",
    "-f",
    help="Expected fingerprint (hex string). If provided, will check if this specific fingerprint is present.",
)
def decode(text: str, input_file: str, fingerprint: str):
    """Decode fingerprint from text."""
    try:
        # Get input text
        if input_file:
            with open(input_file, "r", encoding="utf-8") as f:
                text = f.read().strip()
        elif not text:
            text = click.prompt("Enter text to decode")
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
    help="Text to analyze for hidden data",
)
@click.option(
    "--input-file",
    "-i",
    type=click.Path(exists=True),
    help="Read text from file instead of --text option",
)
def analyze(text: str, input_file: str):
    """Analyze text for hidden variation selectors."""
    try:
        # Get input text
        if input_file:
            with open(input_file, "r", encoding="utf-8") as f:
                text = f.read().strip()
        elif not text:
            text = click.prompt("Enter text to analyze")

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
    help="Text to encode secret message into",
)
@click.option(
    "--input-file",
    "-i",
    type=click.Path(exists=True),
    help="Read text from file instead of --text option",
)
@click.option(
    "--output-file",
    "-o",
    type=click.Path(),
    help="Write encoded text to file",
)
@click.option(
    "--message",
    "-m",
    help="Secret message to encode",
)
@click.option(
    "--single-char",
    "-s",
    is_flag=True,
    help="Encode entire message into a single character (Paul Butler's approach)",
)
def hide(text: str, input_file: str, output_file: str, message: str, single_char: bool):
    """Hide a secret message in text using variation selectors."""
    try:
        # Get input text
        if input_file:
            with open(input_file, "r", encoding="utf-8") as f:
                text = f.read().strip()
        elif not text:
            text = click.prompt("Enter text to encode message into")

        # Get message
        if not message:
            message = click.prompt("Enter secret message")

        if single_char:
            if len(text) != 1:
                console.print(
                    "[bold red]Error:[/bold red] Single-char mode requires exactly one character as text"
                )
                sys.exit(1)
            encoded_text = encode_message_in_single_char(text, message)
        else:
            encoded_text = encode_message_in_text(text, message)

        # Output results
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(encoded_text)
            console.print(f"[green]✓[/green] Encoded text written to: {output_file}")

        console.print(
            Panel(
                f"[bold green]Message hidden successfully![/bold green]\n\n"
                f"[bold]Original text:[/bold] {text}\n"
                f"[bold]Secret message:[/bold] {message}\n"
                f"[bold]Encoded text:[/bold] {encoded_text if not output_file else f'(written to {output_file})'}",
                title="Hide Message Result",
                border_style="green",
            )
        )

        # Also show the encoded text alone for easy copying if not writing to file
        if not output_file:
            console.print(f"\n[bold]Encoded text (copy this):[/bold]\n{encoded_text}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@main.command()
@click.option(
    "--text",
    "-t",
    help="Text to decode secret message from",
)
@click.option(
    "--input-file",
    "-i",
    type=click.Path(exists=True),
    help="Read text from file instead of --text option",
)
@click.option(
    "--single-char",
    "-s",
    is_flag=True,
    help="Decode message from a single character (Paul Butler's approach)",
)
def reveal(text: str, input_file: str, single_char: bool):
    """Reveal a secret message hidden in text."""
    try:
        # Get input text
        if input_file:
            with open(input_file, "r", encoding="utf-8") as f:
                text = f.read().strip()
        elif not text:
            text = click.prompt("Enter text to reveal message from")

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


@main.command()
@click.option(
    "--private-key",
    "-k",
    default="pawpad_private.pem",
    help="Path to save private key (default: pawpad_private.pem)",
)
@click.option(
    "--public-key",
    "-p",
    default="pawpad_public.pem",
    help="Path to save public key (default: pawpad_public.pem)",
)
def keygen(private_key: str, public_key: str):
    """Generate RSA key pair for cryptographic signing."""
    try:
        private_key_pem, public_key_pem = generate_key_pair()
        save_key_pair(private_key_pem, public_key_pem, private_key, public_key)

        console.print(
            Panel(
                f"[bold green]Key pair generated successfully![/bold green]\n\n"
                f"[bold]Private key:[/bold] {private_key}\n"
                f"[bold]Public key:[/bold] {public_key}\n\n"
                f"[yellow]⚠️  Keep your private key secure![/yellow]",
                title="Key Generation Result",
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
    help="Text to sign with chained fingerprints",
)
@click.option(
    "--input-file",
    "-i",
    type=click.Path(exists=True),
    help="Read text from file instead of --text option",
)
@click.option(
    "--output-file",
    "-o",
    type=click.Path(),
    help="Write signed text to file",
)
@click.option(
    "--private-key",
    "-k",
    default="pawpad_private.pem",
    help="Path to private key file (default: pawpad_private.pem)",
)
def sign(text: str, input_file: str, output_file: str, private_key: str):
    """Sign text with chained cryptographic fingerprints for tampering detection."""
    try:
        # Get input text
        if input_file:
            with open(input_file, "r", encoding="utf-8") as f:
                text = f.read().strip()
        elif not text:
            text = click.prompt("Enter text to sign")

        if not os.path.exists(private_key):
            console.print(
                f"[bold red]Error:[/bold red] Private key file not found: {private_key}"
            )
            console.print("Run 'pawpad keygen' to generate a key pair first.")
            sys.exit(1)

        private_key_pem = load_private_key(private_key)
        signed_text = sign_text_with_chained_fingerprints(text, private_key_pem)

        # Output results
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(signed_text)
            console.print(f"[green]✓[/green] Signed text written to: {output_file}")

        console.print(
            Panel(
                f"[bold green]Text signed successfully![/bold green]\n\n"
                f"[bold]Original text:[/bold] {text}\n"
                f"[bold]Signed text:[/bold] {signed_text if not output_file else f'(written to {output_file})'}\n\n"
                f"[dim]Each character now has a unique cryptographic fingerprint[/dim]",
                title="Sign Result",
                border_style="green",
            )
        )

        # Also show the signed text alone for easy copying if not writing to file
        if not output_file:
            console.print(f"\n[bold]Signed text (copy this):[/bold]\n{signed_text}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@main.command()
@click.option(
    "--text",
    "-t",
    help="Signed text to verify for tampering",
)
@click.option(
    "--input-file",
    "-i",
    type=click.Path(exists=True),
    help="Read signed text from file instead of --text option",
)
@click.option(
    "--private-key",
    "-k",
    default="pawpad_private.pem",
    help="Path to private key file (default: pawpad_private.pem)",
)
def verify(text: str, input_file: str, private_key: str):
    """Verify signed text and detect tampering."""
    try:
        # Get input text
        if input_file:
            with open(input_file, "r", encoding="utf-8") as f:
                text = f.read().strip()
        elif not text:
            text = click.prompt("Enter signed text to verify")

        if not os.path.exists(private_key):
            console.print(
                f"[bold red]Error:[/bold red] Private key file not found: {private_key}"
            )
            console.print("Run 'pawpad keygen' to generate a key pair first.")
            sys.exit(1)

        private_key_pem = load_private_key(private_key)
        result = verify_chained_fingerprints(text, private_key_pem)

        # Create a detailed analysis table
        table = Table(title="Verification Analysis")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Valid", "✓ Yes" if result["is_valid"] else "✗ No")
        table.add_row("Original Text", result["original_text"])
        table.add_row("Total Characters", str(result["total_characters"]))
        table.add_row("Signed Characters", str(result["signed_characters"]))

        if result["tampered_positions"]:
            table.add_row("Tampered Positions", str(result["tampered_positions"]))
            table.add_row("Tampered Characters", str(result["tampered_characters"]))

        console.print(table)

        # Show the main result
        if result["is_valid"]:
            console.print(
                Panel(
                    f"[bold green]{result['analysis']}[/bold green]",
                    title="Verification Result",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    f"[bold red]{result['analysis']}[/bold red]\n\n"
                    f"[yellow]The text has been modified after signing.[/yellow]",
                    title="Verification Result",
                    border_style="red",
                )
            )

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@main.command()
@click.option(
    "--text",
    "-t",
    help="Signed text to extract original text from",
)
@click.option(
    "--input-file",
    "-i",
    type=click.Path(exists=True),
    help="Read signed text from file instead of --text option",
)
@click.option(
    "--output-file",
    "-o",
    type=click.Path(),
    help="Write extracted text to file",
)
def extract(text: str, input_file: str, output_file: str):
    """Extract original text from signed text (removes signatures)."""
    try:
        # Get input text
        if input_file:
            with open(input_file, "r", encoding="utf-8") as f:
                text = f.read().strip()
        elif not text:
            text = click.prompt("Enter signed text to extract original from")

        original_text = extract_original_text_from_signed(text)

        # Output results
        if output_file:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(original_text)
            console.print(f"[green]✓[/green] Extracted text written to: {output_file}")

        console.print(
            Panel(
                f"[bold green]Original text extracted![/bold green]\n\n"
                f"[bold]Signed text:[/bold] {text}\n"
                f"[bold]Original text:[/bold] {original_text if not output_file else f'(written to {output_file})'}",
                title="Extract Result",
                border_style="green",
            )
        )

        # Also show the original text alone for easy copying if not writing to file
        if not output_file:
            console.print(f"\n[bold]Original text (copy this):[/bold]\n{original_text}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
