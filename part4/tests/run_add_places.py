#!/usr/bin/env python3
"""
Runner script to execute add_places.py
"""
from add_places import add_sample_places

if __name__ == "__main__":
    print("Starting to add places to the database...")
    add_sample_places()
    print("Process completed.")
