{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  buildInputs = with pkgs; [
    (pkgs.python314.withPackages (python-pkgs: with python314Packages; [
      google-genai
      pillow
      rich
      prompt-toolkit
      requests
      aiohttp
      aiodns
      markdownify
      selenium
      beautifulsoup4
      platformdirs
      build
      twine
    ]))
    geckodriver
    firefox
  ];
}
