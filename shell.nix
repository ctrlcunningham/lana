{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = with pkgs; [
    (pkgs.python314.withPackages (python-pkgs: with python314Packages; [
      google-genai
      pillow
      python-dotenv
      rich
      requests
      aiohttp
      aiodns
      markdownify
    ]))
  ];
}
