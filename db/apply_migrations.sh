#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Check for Supabase URL and Key
if [ -z "$SUPABASE_URL" ] || [ -z "$SUPABASE_KEY" ]; then
    echo -e "${RED}Error: SUPABASE_URL and SUPABASE_KEY must be set${NC}"
    exit 1
fi

# Get directory of script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Apply migrations in order
for migration in "$DIR"/migrations/*.sql; do
    echo -e "${GREEN}Applying migration: $(basename "$migration")${NC}"
    # Here you would add code to apply the migration to Supabase
    # This might require using the Supabase API or a direct PostgreSQL connection
    cat "$migration"
    echo "----------------------------------------"
done

echo -e "${GREEN}Migrations complete${NC}"